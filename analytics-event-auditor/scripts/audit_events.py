#!/usr/bin/env python3
"""Audit captured analytics events against a tracking spec (tool-agnostic).

Usage:
  python audit_events.py --spec spec.csv --events capture.har export.json ... \
      [--platform android] [--expect app_id=TEST_123 ...] [--flow "a,b,c"] [--dup-window 2] \
      [--hosts "extra-host,another"] [--name-key K] [--attr-key K] [--json out.json] [--xlsx out.xlsx]

Spec: CSV/XLSX, one row per attribute: event, trigger, platforms, attribute, type, required, allowed_values, notes
Events: HAR, JSON (Segment/Amplitude/Mixpanel/generic), CSV exports.
PII values are always masked in output.
"""
import argparse
import base64
import csv
import difflib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from urllib.parse import parse_qsl, urlparse

NAME_KEYS = ["event", "event_type", "eventName", "event_name", "e", "en", "action", "name"]
ATTR_KEYS = ["properties", "event_properties", "params", "attributes", "attrs", "eventAttributes",
             "event_attributes", "a", "data"]
USER_KEYS = ["user_id", "userId", "distinct_id", "uid", "customer_id", "customerId", "anonymousId",
             "anonymous_id", "device_id", "deviceId", "cid", "client_id"]
TS_KEYS = ["timestamp", "time", "ts", "event_time", "client_ts", "created_at", "eventTime", "sentAt"]
PLATFORM_KEYS = ["platform", "os", "os_name", "$os", "device_platform"]
VOLATILE = {"timestamp", "time", "ts", "event_time", "client_ts", "created_at", "event_id", "insert_id",
            "$insert_id", "message_id", "messageId", "session_id", "sessionId", "eventTime", "sentAt", "_ts"}
SDK_EVENT_PATTERNS = [r"^MOE_", r"^\$", r"^ce_", r"^App (Opened|Launched|Installed)", r"^Application ",
                      r"^(session_start|first_open|user_engagement|screen_view|page_view|app_open|app_update)$",
                      r"^\[Amplitude\]", r"^Notification ", r"^UTM Visited$", r"^Device Uninstalled$"]
DEFAULT_HOSTS = ["moengage", "amplitude", "mixpanel", "segment.io", "segment.com", "google-analytics",
                 "analytics.google", "googletagmanager", "clevertap", "wzrkt", "webengage", "firebaselogging",
                 "app-measurement", "braze", "appboy", "appsflyer", "branch.io", "rudderstack", "posthog",
                 "heapanalytics", "mparticle", "netcore", "smartech"]

# ---------------- PII ----------------
PII_KEY_RULES = [
    ("email", re.compile(r"e[-_]?mail", re.I)),
    ("phone", re.compile(r"phone|mobile|msisdn|contact[-_]?no|whatsapp", re.I)),
    ("name", re.compile(r"(^|[-_.])(first|last|full|user|customer)?[-_]?name$", re.I)),
    ("address", re.compile(r"address|street|house[-_]?no|landmark", re.I)),
    ("dob", re.compile(r"(^|[-_])dob($|[-_])|birth", re.I)),
    ("gov_id", re.compile(r"aadhaa?r|(^|[-_])pan($|[-_])|ssn|passport|national[-_]?id", re.I)),
    ("payment", re.compile(r"card[-_]?(no|num)|cvv|iban|account[-_]?(no|num)|upi[-_]?id|vpa", re.I)),
    ("secret", re.compile(r"password|passwd|otp|token|secret|api[-_]?key|auth", re.I)),
    ("precise_location", re.compile(r"^(lat|latitude|lng|lon|longitude)$", re.I)),
]
NOT_PII_NAME_KEYS = re.compile(r"(product|item|category|screen|page|event|campaign|plan|coupon|variant|"
                               r"experiment|city|brand|button|tab|section|file|app|sku)[-_]?name$", re.I)
PII_VALUE_RULES = [
    ("email", re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")),
    ("phone", re.compile(r"^(\+?91[-\s]?|0)?[6-9]\d{9}$")),
    ("phone", re.compile(r"^\+\d{10,15}$")),
    ("gov_id", re.compile(r"^[A-Z]{5}\d{4}[A-Z]$")),             # PAN
    ("gov_id", re.compile(r"^\d{4}\s?\d{4}\s?\d{4}$")),          # Aadhaar-like 12 digits
    ("secret", re.compile(r"^eyJ[\w-]+\.[\w-]+\.[\w-]+$")),      # JWT
    ("ip_address", re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")),
]


def luhn_ok(digits):
    s, alt = 0, False
    for d in reversed(digits):
        n = int(d)
        if alt:
            n = n * 2 - 9 if n * 2 > 9 else n * 2
        s += n
        alt = not alt
    return s % 10 == 0


def mask(v):
    s = str(v)
    if "@" in s:
        local, _, dom = s.partition("@")
        return f"{local[:1]}***@{dom[:1]}***"
    if len(s) <= 4:
        return "*" * len(s)
    return f"{s[:2]}{'*' * min(len(s) - 4, 8)}{s[-2:]}"


def pii_hits(attrs, path=""):
    hits = []
    if isinstance(attrs, dict):
        for k, v in attrs.items():
            p = f"{path}.{k}" if path else str(k)
            if isinstance(v, (dict, list)):
                hits += pii_hits(v, p)
                continue
            if v in (None, "", [], {}):
                continue
            key_kind = None
            if not NOT_PII_NAME_KEYS.search(str(k)):
                for kind, rx in PII_KEY_RULES:
                    if rx.search(str(k)):
                        key_kind = kind
                        break
            val_kind = None
            sv = str(v).strip()
            for kind, rx in PII_VALUE_RULES:
                if rx.match(sv):
                    val_kind = kind
                    break
            digits = re.sub(r"[\s-]", "", sv)
            if not val_kind and digits.isdigit() and 13 <= len(digits) <= 19 and luhn_ok(digits):
                val_kind = "payment"
            if key_kind == "secret" and isinstance(v, bool):
                key_kind = None  # e.g. otp_verified: true
            if key_kind or val_kind:
                hits.append({"path": p, "kind": key_kind or val_kind,
                             "by": "key+value" if key_kind and val_kind else ("key" if key_kind else "value"),
                             "sample": mask(v)})
    elif isinstance(attrs, list):
        for i, v in enumerate(attrs):
            hits += pii_hits(v, f"{path}[{i}]")
    return hits


# ---------------- Spec ----------------
def read_table(path):
    if path.lower().endswith((".xlsx", ".xlsm")):
        from openpyxl import load_workbook
        ws = load_workbook(path, read_only=True, data_only=True).active
        rows = list(ws.iter_rows(values_only=True))
        hdr = [str(h or "").strip() for h in rows[0]]
        return [dict(zip(hdr, ["" if x is None else x for x in r])) for r in rows[1:]]
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def norm_hdr(row):
    return {re.sub(r"[^a-z]", "", str(k).lower()): v for k, v in row.items()}


def load_spec(path):
    spec = {}
    for raw in read_table(path):
        r = norm_hdr(raw)
        ev = str(r.get("event") or r.get("eventname") or "").strip()
        if not ev:
            continue
        e = spec.setdefault(ev, {"platforms": set(), "trigger": "", "attrs": {}})
        plats = str(r.get("platforms") or r.get("platform") or "")
        e["platforms"] |= {p.strip().lower() for p in re.split(r"[|,/]", plats) if p.strip()}
        e["trigger"] = e["trigger"] or str(r.get("trigger") or "")
        attr = str(r.get("attribute") or r.get("attributename") or r.get("property") or "").strip()
        if attr:
            req = str(r.get("required") or "yes").strip().lower()
            allowed = str(r.get("allowedvalues") or r.get("values") or "").strip()
            e["attrs"][attr] = {
                "type": str(r.get("type") or r.get("datatype") or "string").strip().lower(),
                "required": req in ("yes", "y", "true", "1", "required", "mandatory"),
                "allowed": [a.strip() for a in allowed.split("|") if a.strip()] if allowed else [],
            }
    return spec


# ---------------- Event extraction ----------------
def first(d, keys):
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return None


def scalars(d):
    return {k: v for k, v in d.items() if not isinstance(v, (dict, list))}


def walk(obj, ctx, out, name_keys, attr_keys):
    if isinstance(obj, list):
        for x in obj:
            walk(x, ctx, out, name_keys, attr_keys)
        return
    if not isinstance(obj, dict):
        return
    name_key = next((k for k in name_keys if isinstance(obj.get(k), str) and obj.get(k)), None)
    attr_key = next((k for k in attr_keys if isinstance(obj.get(k), dict)), None)
    # "name" alone is too generic (product names etc.): require an attributes object alongside it.
    if name_key and (name_key != "name" or attr_key):
        attrs = dict(obj.get(attr_key) or {}) if attr_key else {
            k: v for k, v in obj.items() if k != name_key and k not in USER_KEYS + TS_KEYS + PLATFORM_KEYS}
        user = first(obj, USER_KEYS) or first(attrs, USER_KEYS) or first(ctx, USER_KEYS)
        ts = first(obj, TS_KEYS) or first(attrs, TS_KEYS) or first(ctx, TS_KEYS)
        plat = first(obj, PLATFORM_KEYS) or first(attrs, PLATFORM_KEYS) or first(ctx, PLATFORM_KEYS)
        user_props = obj.get("user_properties") or obj.get("userProperties") or obj.get("traits") or {}
        envelope = {k: v for k, v in obj.items() if k not in (attr_key, name_key)}
        out.append({"name": obj[name_key], "attrs": attrs, "user": user, "ts": ts, "platform": plat,
                    "context": {**ctx, **scalars(obj)}, "user_props": user_props if isinstance(user_props, dict) else {},
                    "envelope": envelope})
        return
    new_ctx = {**ctx, **scalars(obj)}
    for v in obj.values():
        if isinstance(v, (dict, list)):
            walk(v, new_ctx, out, name_keys, attr_keys)


def parse_body(text):
    """Return a JSON-ish object from a request body: JSON, form-encoded (incl. base64 'data'), or None."""
    if text is None:
        return None
    t = text.strip()
    if not t:
        return None
    if t[0] in "[{":
        try:
            return json.loads(t)
        except json.JSONDecodeError:
            pass
    if "=" in t:
        form = dict(parse_qsl(t, keep_blank_values=True))
        for k in ("data", "e", "events", "batch", "payload"):
            if k in form:
                v = form[k]
                for cand in (v, _b64(v)):
                    if cand and cand.strip()[:1] in "[{":
                        try:
                            parsed = json.loads(cand)
                            return {**{x: y for x, y in form.items() if x != k}, k: parsed}
                        except json.JSONDecodeError:
                            pass
        return form
    b = _b64(t)
    if b and b.strip()[:1] in "[{":
        try:
            return json.loads(b)
        except json.JSONDecodeError:
            return None
    return None


def _b64(s):
    try:
        return base64.b64decode(s + "=" * (-len(s) % 4)).decode("utf-8")
    except Exception:
        return None


def ga4_events(url, body):
    q = dict(parse_qsl(urlparse(url).query))
    lines = [ln for ln in (body or "").splitlines() if ln.strip()] or [""]
    out = []
    for ln in lines:
        p = {**q, **dict(parse_qsl(ln))}
        if "en" not in p:
            continue
        attrs = {}
        for k, v in p.items():
            if k.startswith("ep."):
                attrs[k[3:]] = v
            elif k.startswith("epn."):
                try:
                    attrs[k[4:]] = float(v) if "." in v else int(v)
                except ValueError:
                    attrs[k[4:]] = v
        out.append({"name": p["en"], "attrs": attrs, "user": p.get("uid") or p.get("cid"), "ts": None,
                    "platform": "web", "context": {"url": url, "tid": p.get("tid")}, "user_props": {}})
    return out


def load_har(path, hosts, name_keys, attr_keys):
    with open(path, encoding="utf-8") as fh:
        har = json.load(fh)
    out = []
    for ent in har.get("log", {}).get("entries", []):
        req = ent.get("request", {})
        url = req.get("url", "")
        if not any(h in url.lower() for h in hosts):
            continue
        body = (req.get("postData") or {}).get("text")
        if "collect" in url and ("en=" in url or (body and "en=" in body)):
            out += ga4_events(url, body)
            continue
        hdrs = {h.get("name", "").lower(): h.get("value", "") for h in req.get("headers", [])}
        ctx = {"url": url, **dict(parse_qsl(urlparse(url).query)),
               **{k: v for k, v in hdrs.items() if any(x in k for x in ("app", "key", "workspace", "project"))}}
        obj = parse_body(body)
        if obj is None:
            continue
        found = []
        walk(obj, ctx, found, name_keys, attr_keys)
        for f in found:
            f["ts"] = f["ts"] or ent.get("startedDateTime")
        out += found
    return out


def load_csv_events(path):
    rows = read_table(path)
    out = []
    if not rows:
        return out
    cols = list(rows[0].keys())
    lc = {re.sub(r"[^a-z]", "", c.lower()): c for c in cols}
    name_col = next((lc[k] for k in ("eventname", "event", "eventtype", "name", "action") if k in lc), None)
    if not name_col:
        sys.exit(f"{path}: no event-name column found (columns: {cols})")
    props_col = next((lc[k] for k in ("properties", "attributes", "eventattributes", "eventproperties", "params") if k in lc), None)
    meta = {name_col, props_col} | {lc[k] for k in lc if k in {re.sub(r'[^a-z]', '', x.lower()) for x in USER_KEYS + TS_KEYS + PLATFORM_KEYS}}
    for r in rows:
        if props_col and r.get(props_col):
            try:
                attrs = json.loads(r[props_col])
            except json.JSONDecodeError:
                attrs = {"_raw": r[props_col]}
        else:
            attrs = {c: _coerce(r[c]) for c in cols if c not in meta and r.get(c) not in (None, "")}
        nr = {re.sub(r"[^a-z]", "", k.lower()): v for k, v in r.items()}
        out.append({"name": r[name_col], "attrs": attrs, "untyped": not props_col,
                    "user": first(nr, [re.sub(r"[^a-z]", "", k.lower()) for k in USER_KEYS]),
                    "ts": first(nr, [re.sub(r"[^a-z]", "", k.lower()) for k in TS_KEYS]),
                    "platform": first(nr, [re.sub(r"[^a-z]", "", k.lower()) for k in PLATFORM_KEYS]),
                    "context": {k: v for k, v in r.items() if k not in (props_col,)}, "user_props": {}})
    return out


def _coerce(v):
    """CSV loses types: restore numbers/bools so they aren't all reported as type mismatches.
    Leading-zero numbers (postal codes, phone-like ids) stay strings."""
    if not isinstance(v, str):
        return v
    s = v.strip()
    if s.lower() in ("true", "false"):
        return s.lower() == "true"
    if re.fullmatch(r"-?(0|[1-9]\d*)", s):
        return int(s)
    if re.fullmatch(r"-?(0|[1-9]\d*)\.\d+", s):
        return float(s)
    return v


def load_events(paths, args):
    hosts = DEFAULT_HOSTS + [h.strip().lower() for h in (args.hosts or "").split(",") if h.strip()]
    name_keys = ([args.name_key] if args.name_key else []) + NAME_KEYS
    attr_keys = ([args.attr_key] if args.attr_key else []) + ATTR_KEYS
    events = []
    for p in paths:
        pl = p.lower()
        if pl.endswith(".har"):
            evs = load_har(p, hosts, name_keys, attr_keys)
        elif pl.endswith((".csv", ".xlsx")):
            evs = load_csv_events(p)
        else:
            with open(p, encoding="utf-8") as fh:
                txt = fh.read()
            try:
                obj = json.loads(txt)
            except json.JSONDecodeError:  # NDJSON
                obj = [json.loads(ln) for ln in txt.splitlines() if ln.strip()]
            evs = []
            walk(obj, {}, evs, name_keys, attr_keys)
        for e in evs:
            e["source"] = os.path.basename(p)
        events += evs
    if args.platform:
        want = args.platform.lower()
        events = [e for e in events if not e["platform"] or want in str(e["platform"]).lower()]
    return events


# ---------------- Checks ----------------
def norm_name(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def is_sdk_event(name):
    return any(re.search(p, name) for p in SDK_EVENT_PATTERNS)


def name_style(n):
    if re.fullmatch(r"[a-z0-9]+(_[a-z0-9]+)+", n): return "snake_case"
    if re.fullmatch(r"[a-z]+([A-Z][a-z0-9]*)+", n): return "camelCase"
    if re.fullmatch(r"([A-Z][a-z0-9]*){2,}", n): return "PascalCase"
    if re.fullmatch(r"[A-Z0-9]+(_[A-Z0-9]+)+", n): return "UPPER_SNAKE"
    if re.fullmatch(r"[A-Za-z0-9]+( [A-Za-z0-9]+)+", n): return "Title/space separated"
    if re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)+", n): return "kebab-case"
    return "single word/other"


def type_issue(expected, v):
    if v is None:
        return None
    t = expected
    if t in ("string", "str", "text"):
        return None if isinstance(v, str) else f"expected string, got {type(v).__name__}"
    if t in ("int", "integer", "long"):
        if isinstance(v, bool) or not isinstance(v, int):
            if isinstance(v, float) and v.is_integer():
                return "expected int, got float with .0"
            if isinstance(v, str) and re.fullmatch(r"-?\d+", v.strip()):
                return "expected int, got numeric string"
            return f"expected int, got {type(v).__name__}"
        return None
    if t in ("number", "float", "double", "decimal"):
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            if isinstance(v, str) and re.fullmatch(r"-?\d+(\.\d+)?", v.strip()):
                return "expected number, got numeric string"
            return f"expected number, got {type(v).__name__}"
        return None
    if t in ("bool", "boolean"):
        if isinstance(v, bool):
            return None
        return "expected bool, got string 'true/false'" if str(v).lower() in ("true", "false") else f"expected bool, got {type(v).__name__}"
    if t in ("datetime", "date", "timestamp"):
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return None
        if isinstance(v, str) and re.match(r"^\d{4}-\d{2}-\d{2}", v):
            return None
        return f"expected datetime (ISO or epoch), got {v!r}"[:80]
    if t in ("array", "list"):
        return None if isinstance(v, list) else f"expected array, got {type(v).__name__}"
    if t in ("object", "map", "dict", "json"):
        return None if isinstance(v, dict) else f"expected object, got {type(v).__name__}"
    return None


def to_epoch(ts):
    if ts is None or ts == "":
        return None
    if isinstance(ts, (int, float)):
        return ts / 1000 if ts > 1e11 else ts
    s = str(ts).strip()
    if re.fullmatch(r"\d+(\.\d+)?", s):
        return to_epoch(float(s))
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def audit(spec, events, args):
    res = {"summary": {}, "events": [], "attributes": [], "pii": [], "duplicates": [], "flow": [],
           "expect": [], "unexpected": [], "sdk_events": [], "style": [], "spec_issues": []}
    by_name = defaultdict(list)
    for e in events:
        by_name[e["name"]].append(e)
    observed = set(by_name)
    spec_names = set(spec)
    want_platform = (args.platform or "").lower()

    # --- spec issues
    nmap = defaultdict(list)
    for n in spec_names:
        nmap[norm_name(n)].append(n)
    for k, v in nmap.items():
        if len(v) > 1:
            res["spec_issues"].append(f"Event spelled differently in spec: {', '.join(sorted(v))}")
    for ev, s in spec.items():
        for a in s["attrs"]:
            h = pii_hits({a: "x"})
            if h:
                res["spec_issues"].append(f"Spec plans a PII attribute: {ev}.{a} ({h[0]['kind']})")

    # --- event coverage & naming
    matched = {}  # spec name -> observed name
    used_obs = set()
    for sn in sorted(spec_names):
        if want_platform and spec[sn]["platforms"] and not any(want_platform in p for p in spec[sn]["platforms"]):
            res["events"].append({"spec_event": sn, "status": "not in scope for platform", "observed_as": "", "count": 0})
            continue
        if sn in observed:
            matched[sn] = sn
            used_obs.add(sn)
            res["events"].append({"spec_event": sn, "status": "found", "observed_as": sn, "count": len(by_name[sn])})
            continue
        cand = [o for o in observed if norm_name(o) == norm_name(sn) and o not in used_obs]
        if cand:
            o = cand[0]
            matched[sn] = o
            used_obs.add(o)
            res["events"].append({"spec_event": sn, "status": "name mismatch (case/separator)", "observed_as": o,
                                  "count": len(by_name[o])})
            continue
        close = difflib.get_close_matches(sn, [o for o in observed if o not in used_obs and not is_sdk_event(o)], n=1, cutoff=0.75)
        if close:
            o = close[0]
            matched[sn] = o
            used_obs.add(o)
            res["events"].append({"spec_event": sn, "status": "possible rename", "observed_as": o, "count": len(by_name[o])})
            continue
        res["events"].append({"spec_event": sn, "status": "missing", "observed_as": "", "count": 0})

    for o in sorted(observed - used_obs):
        (res["sdk_events"] if is_sdk_event(o) else res["unexpected"]).append({"event": o, "count": len(by_name[o])})

    # --- attributes
    for sn, o in matched.items():
        sattrs = spec[sn]["attrs"]
        occ = by_name[o]
        issues = Counter()
        samples = {}
        extra = Counter()
        for e in occ:
            attrs = e["attrs"] or {}
            for a, rule in sattrs.items():
                if a not in attrs:
                    alt = next((k for k in attrs if norm_name(k) == norm_name(a)), None)
                    if alt:
                        key = (a, f"key name mismatch: sent as '{alt}'")
                        issues[key] += 1
                        v = attrs[alt]
                    elif rule["required"]:
                        issues[(a, "missing (required)")] += 1
                        continue
                    else:
                        issues[(a, "missing (optional)")] += 1
                        continue
                else:
                    v = attrs[a]
                if v is None or v == "" or v == [] or v == {}:
                    issues[(a, "null/empty value")] += 1
                    continue
                ti = type_issue(rule["type"], v)
                if ti:
                    issues[(a, ti)] += 1
                    samples.setdefault((a, ti), v)
                if rule["allowed"] and str(v) not in rule["allowed"]:
                    k = (a, f"value not in allowed set {rule['allowed']}")
                    issues[k] += 1
                    samples.setdefault(k, v)
            for k in attrs:
                if (k not in sattrs and not any(norm_name(k) == norm_name(a) for a in sattrs)
                        and k not in VOLATILE and k not in USER_KEYS and k not in PLATFORM_KEYS):
                    extra[k] += 1
        for (a, msg), c in sorted(issues.items()):
            s = samples.get((a, msg))
            sample = mask(s) if s is not None and pii_hits({a: s}) else (repr(s)[:40] if s is not None else "")
            res["attributes"].append({"event": sn, "observed_as": o, "attribute": a, "issue": msg,
                                      "occurrences": f"{c}/{len(occ)}", "sample": sample})
        for k, c in sorted(extra.items()):
            res["attributes"].append({"event": sn, "observed_as": o, "attribute": k, "issue": "extra (not in spec)",
                                      "occurrences": f"{c}/{len(occ)}", "sample": ""})

    # --- PII (all events, event attrs + user props)
    seen = set()
    for e in events:
        env = {k: v for k, v in (e.get("envelope") or {}).items() if k not in USER_KEYS}
        for where, d in (("event", e["attrs"]), ("user", e.get("user_props") or {}), ("envelope", env)):
            for h in pii_hits(d):
                key = (e["name"], where, h["path"], h["kind"])
                if key in seen:
                    continue
                seen.add(key)
                leaf = h["path"].split(".")[-1]
                note = ""
                if h["by"] == "value" and re.search(r"(^|_)(id|no|num|number|code|ref)$|Id$", leaf):
                    note = "likely false positive (id-like key): verify"
                if where == "user" and any(x["event"] == e["name"] and x["path"] == h["path"] for x in res["pii"]):
                    continue
                res["pii"].append({"event": e["name"], "scope": where, **h, "note": note})

    # --- duplicates
    groups = defaultdict(list)
    for e in events:
        sig = json.dumps({k: v for k, v in (e["attrs"] or {}).items() if k not in VOLATILE}, sort_keys=True, default=str)
        groups[(e["name"], str(e["user"]), sig)].append(e)
    no_ts = 0
    for (name, user, _), evs in groups.items():
        if len(evs) < 2:
            continue
        times = sorted(t for t in (to_epoch(x["ts"]) for x in evs) if t is not None)
        if len(times) < 2:
            no_ts += 1
            continue
        dups = sum(1 for a, b in zip(times, times[1:]) if b - a <= args.dup_window)
        if dups:
            res["duplicates"].append({"event": name, "user": mask(user) if user and user != "None" else "",
                                      "duplicate_fires": dups, "window_s": args.dup_window})
    if no_ts:
        res["duplicates"].append({"event": "(note)", "user": "", "duplicate_fires": no_ts,
                                  "window_s": "identical events without timestamps: check manually"})

    # --- flow
    if args.flow:
        flow = [f.strip() for f in args.flow.split(",") if f.strip()]
        alias = {sn: matched.get(sn, sn) for sn in flow}
        per_user = defaultdict(list)
        for e in sorted(events, key=lambda x: to_epoch(x["ts"]) or 0):
            per_user[str(e["user"])].append(e["name"])
        flow_names = set(alias.values())
        for user, seq in per_user.items():
            if not flow_names & set(seq):
                continue  # user never entered this flow (e.g. a different SDK's anonymous id)
            pos = []
            for step in flow:
                nm = alias[step]
                pos.append(seq.index(nm) if nm in seq else None)
            missing = [flow[i] for i, p in enumerate(pos) if p is None]
            present = [(flow[i], p) for i, p in enumerate(pos) if p is not None]
            out_of_order = [f"{a}→{b}" for (a, pa), (b, pb) in zip(present, present[1:]) if pb < pa]
            if missing or out_of_order:
                res["flow"].append({"user": mask(user) if user != "None" else "", "missing_steps": ", ".join(missing),
                                    "out_of_order": ", ".join(out_of_order)})

    # --- expectations (workspace/env/app id)
    for exp in args.expect or []:
        k, _, want = exp.partition("=")
        mism = Counter()
        checked = 0
        for e in events:
            ctx = {**e.get("context", {}), **(e["attrs"] or {})}
            if k == "url":
                got = ctx.get("url", "")
                checked += 1
                if want not in got:
                    mism[urlparse(got).netloc + urlparse(got).path[:40]] += 1
            elif k in ctx:
                checked += 1
                if str(ctx[k]) != want:
                    mism[str(ctx[k])] += 1
        res["expect"].append({"expect": exp, "events_checked": checked,
                              "mismatches": sum(mism.values()),
                              "observed_values": ", ".join(f"{v} ({c})" for v, c in mism.most_common(5)) if mism else "",
                              "note": "" if checked else "key not found in any event/context"})

    # --- naming style
    obs_custom = [n for n in observed if not is_sdk_event(n)]
    styles = Counter(name_style(n) for n in obs_custom)
    if len([s for s in styles if s != "single word/other"]) > 1:
        res["style"].append({"what": "event names", "styles": dict(styles),
                             "examples": {s: [n for n in obs_custom if name_style(n) == s][:3] for s in styles}})
    akeys = {k for e in events if not is_sdk_event(e["name"]) for k in (e["attrs"] or {})}
    astyles = Counter(name_style(k) for k in akeys)
    if len([s for s in astyles if s != "single word/other"]) > 1:
        res["style"].append({"what": "attribute keys", "styles": dict(astyles),
                             "examples": {s: sorted(k for k in akeys if name_style(k) == s)[:3] for s in astyles}})

    if any(e.get("untyped") for e in events):
        res["notes"] = ["Some events came from a flat CSV export: values were type-coerced, so attribute TYPE checks "
                        "for those events are not reliable. Use a HAR/JSON capture to verify types."]
    st = Counter(x["status"] for x in res["events"])
    in_scope = sum(c for s, c in st.items() if s != "not in scope for platform")
    res["summary"] = {
        "events_captured": len(events), "distinct_events": len(observed), "spec_events": len(spec_names),
        "spec_found_exact": st.get("found", 0),
        "spec_found_with_name_issue": st.get("name mismatch (case/separator)", 0) + st.get("possible rename", 0),
        "spec_missing": st.get("missing", 0),
        "coverage_pct": round(100 * (in_scope - st.get("missing", 0)) / in_scope, 1) if in_scope else None,
        "attribute_issues": len(res["attributes"]), "pii_hits": len(res["pii"]),
        "duplicate_groups": len([d for d in res["duplicates"] if d["event"] != "(note)"]),
        "unexpected_events": len(res["unexpected"]),
        "expectation_mismatches": sum(x["mismatches"] for x in res["expect"]),
    }
    return res


# ---------------- Output ----------------
def md_table(rows, cols):
    if not rows:
        return "_none_\n"
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        out.append("| " + " | ".join(str(r.get(c, "")).replace("|", "\\|").replace("\n", " ") for c in cols) + " |")
    return "\n".join(out) + "\n"


def to_markdown(res):
    s = res["summary"]
    L = ["# Tracking audit", "",
         f"Captured {s['events_captured']} events ({s['distinct_events']} distinct). Spec: {s['spec_events']} events, "
         f"coverage {s['coverage_pct']}% ({s['spec_found_exact']} exact, {s['spec_found_with_name_issue']} with name issues, "
         f"{s['spec_missing']} missing).",
         f"PII hits: {s['pii_hits']} · attribute issues: {s['attribute_issues']} · duplicate groups: {s['duplicate_groups']} · "
         f"unexpected events: {s['unexpected_events']} · expectation mismatches: {s['expectation_mismatches']}", ""]
    for n in res.get("notes", []):
        L += [f"> Note: {n}", ""]
    if res["expect"]:
        L += ["## Environment / workspace expectations", md_table(res["expect"], ["expect", "events_checked", "mismatches", "observed_values", "note"])]
    L += ["## PII (values masked)", md_table(res["pii"], ["event", "scope", "path", "kind", "by", "sample", "note"])]
    L += ["## Spec event coverage", md_table(res["events"], ["spec_event", "status", "observed_as", "count"])]
    L += ["## Attribute issues", md_table(res["attributes"], ["event", "observed_as", "attribute", "issue", "occurrences", "sample"])]
    L += ["## Duplicate fires", md_table(res["duplicates"], ["event", "user", "duplicate_fires", "window_s"])]
    if res["flow"]:
        L += ["## Flow order", md_table(res["flow"], ["user", "missing_steps", "out_of_order"])]
    L += ["## Unexpected events (not in spec)", md_table(res["unexpected"], ["event", "count"])]
    if res["sdk_events"]:
        L += ["## SDK/system events (ignored)", ", ".join(f"{x['event']} ({x['count']})" for x in res["sdk_events"]), ""]
    if res["style"]:
        L += ["## Naming style inconsistencies"]
        for st in res["style"]:
            L.append(f"- {st['what']}: {st['styles']} e.g. {st['examples']}")
        L.append("")
    if res["spec_issues"]:
        L += ["## Spec issues"] + [f"- {x}" for x in res["spec_issues"]] + [""]
    return "\n".join(L)


def to_xlsx(res, path):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    wb = Workbook()
    hdr_font, hdr_fill = Font(name="Arial", bold=True, color="FFFFFF"), PatternFill("solid", fgColor="1F3864")
    sheets = [("Summary", [{"metric": k, "value": v} for k, v in res["summary"].items()], ["metric", "value"]),
              ("PII", res["pii"], ["event", "scope", "path", "kind", "by", "sample", "note"]),
              ("Event Coverage", res["events"], ["spec_event", "status", "observed_as", "count"]),
              ("Attribute Issues", res["attributes"], ["event", "observed_as", "attribute", "issue", "occurrences", "sample"]),
              ("Duplicates", res["duplicates"], ["event", "user", "duplicate_fires", "window_s"]),
              ("Unexpected", res["unexpected"], ["event", "count"]),
              ("Expectations", res["expect"], ["expect", "events_checked", "mismatches", "observed_values", "note"])]
    if res["flow"]:
        sheets.append(("Flow", res["flow"], ["user", "missing_steps", "out_of_order"]))
    first_sheet = True
    for title, rows, cols in sheets:
        ws = wb.active if first_sheet else wb.create_sheet()
        first_sheet = False
        ws.title = title
        ws.append(cols)
        for c in ws[1]:
            c.font, c.fill = hdr_font, hdr_fill
        for r in rows:
            ws.append([str(r.get(c, "")) if isinstance(r.get(c), (list, dict)) else r.get(c, "") for c in cols])
        for i, c in enumerate(cols, start=1):
            ws.column_dimensions[ws.cell(1, i).column_letter].width = 18 if c not in ("issue", "observed_values", "note") else 45
        for row in ws.iter_rows(min_row=2):
            for c in row:
                c.font = Font(name="Arial", size=10)
                c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.freeze_panes = "A2"
    wb.save(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--events", nargs="+", required=True)
    ap.add_argument("--platform")
    ap.add_argument("--expect", action="append", help="key=value expected in every event context, e.g. app_id=TEST; url=substring")
    ap.add_argument("--flow", help="comma-separated expected event order per user")
    ap.add_argument("--dup-window", type=float, default=2.0)
    ap.add_argument("--hosts")
    ap.add_argument("--name-key")
    ap.add_argument("--attr-key")
    ap.add_argument("--json")
    ap.add_argument("--xlsx")
    args = ap.parse_args()

    spec = load_spec(args.spec)
    if not spec:
        sys.exit("Spec has no events (need an 'event' column).")
    events = load_events(args.events, args)
    if not events:
        sys.exit("No events extracted. Check --hosts for HAR files, or --name-key/--attr-key for custom payloads.")
    res = audit(spec, events, args)
    print(to_markdown(res))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, default=str, ensure_ascii=False)
    if args.xlsx:
        to_xlsx(res, args.xlsx)


if __name__ == "__main__":
    main()
