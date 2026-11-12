#!/usr/bin/env python3
"""Summarize a Playwright trace.zip for flaky-test diagnosis.

Usage:
  python parse_pw_trace.py trace.zip [--slow-ms 2000] [--extract-screens OUT_DIR] [--max-actions 200]

Prints:
  - action timeline (relative start, duration, api, selector, error)
  - actions that failed or were slow
  - network requests that failed (>=400 or no response) and slow requests
  - console errors / page errors
  - last log lines of the failing action (Playwright's "waiting for ..." call log)

Tolerant of trace format differences across Playwright versions (before/after events,
legacy "action" events, multiple *.trace files). Uses only the standard library.
"""
import argparse
import json
import os
import sys
import zipfile
from collections import OrderedDict


def read_ndjson(zf, name):
    out = []
    with zf.open(name) as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            try:
                out.append(json.loads(raw))
            except json.JSONDecodeError:
                continue
    return out


def selector_of(params):
    if not isinstance(params, dict):
        return ""
    for key in ("selector", "url", "expression", "name", "key", "text"):
        if key in params and isinstance(params[key], str):
            return params[key]
    return ""


def api_of(ev):
    if ev.get("apiName"):
        return ev["apiName"]
    cls, method = ev.get("class", ""), ev.get("method", "")
    if cls or method:
        return f"{cls}.{method}".strip(".")
    md = ev.get("metadata", {})
    if md:
        return md.get("apiName") or f"{md.get('type', '')}.{md.get('method', '')}".strip(".")
    return "?"


def collect(zf):
    trace_files = [n for n in zf.namelist() if n.endswith(".trace")]
    network_files = [n for n in zf.namelist() if n.endswith(".network")]
    actions = OrderedDict()
    logs = {}
    console = []
    page_errors = []
    screenshots = []
    t0 = None

    for tf in trace_files:
        for ev in read_ndjson(zf, tf):
            typ = ev.get("type")
            if typ == "context-options":
                t0 = ev.get("monotonicTime", t0) if t0 is None else t0
            elif typ == "before":
                cid = ev.get("callId")
                actions[cid] = {
                    "api": api_of(ev),
                    "selector": selector_of(ev.get("params")),
                    "start": ev.get("startTime"),
                    "end": None,
                    "error": None,
                }
            elif typ == "after":
                a = actions.get(ev.get("callId"))
                if a is not None:
                    a["end"] = ev.get("endTime")
                    err = ev.get("error")
                    if err:
                        a["error"] = (err.get("error") or err).get("message") if isinstance(err, dict) else str(err)
            elif typ == "action":  # legacy format
                md = ev.get("metadata", {})
                cid = md.get("id") or len(actions)
                err = md.get("error")
                actions[cid] = {
                    "api": api_of(ev),
                    "selector": selector_of(md.get("params")),
                    "start": md.get("startTime"),
                    "end": md.get("endTime"),
                    "error": (err.get("error") or err).get("message") if isinstance(err, dict) else err,
                }
                for line in md.get("log", []) or []:
                    logs.setdefault(cid, []).append(line)
            elif typ == "log":
                logs.setdefault(ev.get("callId"), []).append(ev.get("message", ""))
            elif typ == "console":
                mtype = ev.get("messageType") or ev.get("params", {}).get("type")
                text = ev.get("text") or ev.get("params", {}).get("text", "")
                if mtype in ("error", "warning"):
                    console.append((ev.get("time"), mtype, text))
            elif typ == "event" and ev.get("method") == "pageError":
                err = ev.get("params", {}).get("error", {})
                msg = err.get("error", {}).get("message") if isinstance(err.get("error"), dict) else err.get("message")
                page_errors.append((ev.get("time"), msg or json.dumps(err)[:200]))
            elif typ == "screencast-frame":
                screenshots.append((ev.get("timestamp"), ev.get("sha1")))

    network = []
    for nf in network_files:
        for ev in read_ndjson(zf, nf):
            if ev.get("type") != "resource-snapshot":
                continue
            snap = ev.get("snapshot", {})
            req, resp = snap.get("request", {}), snap.get("response", {})
            network.append({
                "method": req.get("method", "?"),
                "url": req.get("url", "?"),
                "status": resp.get("status", -1) if resp else -1,
                "time_ms": snap.get("time"),
                "started": snap.get("_monotonicTime") or snap.get("startedDateTime"),
                "failure": (resp or {}).get("_failureText"),
            })

    starts = [a["start"] for a in actions.values() if isinstance(a["start"], (int, float))]
    if t0 is None and starts:
        t0 = min(starts)
    return actions, logs, console, page_errors, network, screenshots, t0 or 0


def fmt_ms(v):
    return f"{v:,.0f}ms" if isinstance(v, (int, float)) else "?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("trace")
    ap.add_argument("--slow-ms", type=float, default=2000)
    ap.add_argument("--max-actions", type=int, default=200)
    ap.add_argument("--extract-screens", metavar="DIR")
    args = ap.parse_args()

    with zipfile.ZipFile(args.trace) as zf:
        actions, logs, console, page_errors, network, screens, t0 = collect(zf)

        print(f"# Trace summary: {os.path.basename(args.trace)}")
        print(f"actions={len(actions)} network={len(network)} console_errors={len(console)} "
              f"page_errors={len(page_errors)} screenshots={len(screens)}\n")

        print("## Action timeline (t=+ms from first action)")
        failed, slow = [], []
        for i, (cid, a) in enumerate(actions.items()):
            dur = (a["end"] - a["start"]) if isinstance(a["end"], (int, float)) and isinstance(a["start"], (int, float)) else None
            rel = (a["start"] - t0) if isinstance(a["start"], (int, float)) else None
            flag = ""
            if a["error"]:
                flag = "  <-- ERROR"
                failed.append((cid, a, dur))
            elif dur is not None and dur >= args.slow_ms:
                flag = "  <-- SLOW"
                slow.append((cid, a, dur))
            if i < args.max_actions:
                sel = f" [{a['selector'][:90]}]" if a["selector"] else ""
                print(f"+{fmt_ms(rel):>10}  {fmt_ms(dur):>9}  {a['api']}{sel}{flag}")
        if len(actions) > args.max_actions:
            print(f"... {len(actions) - args.max_actions} more actions")

        if failed:
            print("\n## Failed actions")
            for cid, a, dur in failed:
                print(f"- {a['api']} [{a['selector']}] after {fmt_ms(dur)}")
                print(f"  error: {str(a['error']).splitlines()[0][:300]}")
                tail = logs.get(cid, [])[-8:]
                if tail:
                    print("  call log (last lines):")
                    for line in tail:
                        print(f"    {line[:200]}")
        if slow:
            print(f"\n## Slow actions (>= {args.slow_ms:.0f}ms)")
            for cid, a, dur in slow:
                print(f"- {a['api']} [{a['selector']}] {fmt_ms(dur)}")

        bad_net = [n for n in network if (isinstance(n["status"], int) and (n["status"] >= 400 or n["status"] <= 0)) or n["failure"]]
        slow_net = [n for n in network if isinstance(n["time_ms"], (int, float)) and n["time_ms"] >= args.slow_ms]
        if bad_net:
            print("\n## Failed network requests")
            for n in bad_net[:50]:
                status = n["failure"] or n["status"]
                print(f"- {n['method']} {n['url'][:150]} -> {status} ({fmt_ms(n['time_ms'])})")
        if slow_net:
            print(f"\n## Slow network requests (>= {args.slow_ms:.0f}ms)")
            for n in sorted(slow_net, key=lambda x: -x["time_ms"])[:20]:
                print(f"- {n['method']} {n['url'][:150]} -> {n['status']} ({fmt_ms(n['time_ms'])})")

        if console:
            print("\n## Console errors/warnings")
            for _, t, text in console[:30]:
                print(f"- [{t}] {text[:250]}")
        if page_errors:
            print("\n## Page errors (uncaught exceptions)")
            for _, msg in page_errors[:20]:
                print(f"- {msg[:250]}")

        if args.extract_screens and screens:
            os.makedirs(args.extract_screens, exist_ok=True)
            names = set(zf.namelist())
            # keep last 10 frames: usually around the failure
            written = 0
            for ts, sha in screens[-10:]:
                for cand in (f"resources/{sha}", sha):
                    if cand in names:
                        dst = os.path.join(args.extract_screens, f"{ts}_{os.path.basename(sha)}")
                        if not dst.endswith((".jpeg", ".jpg", ".png")):
                            dst += ".jpeg"
                        with open(dst, "wb") as out:
                            out.write(zf.read(cand))
                        written += 1
                        break
            print(f"\nExtracted {written} screenshot(s) to {args.extract_screens}")


if __name__ == "__main__":
    try:
        main()
    except zipfile.BadZipFile:
        sys.exit("Not a valid zip. Pass the trace.zip produced by Playwright tracing.")
