#!/usr/bin/env python3
"""Compare the shape of two JSON documents (or two HAR files) and report field-level changes.

Usage:
  python json_shape_diff.py old.json new.json
  python json_shape_diff.py old.har new.har            # compares JSON responses per METHOD + path
  python json_shape_diff.py old.json new.json --json   # machine-readable output

Paths use dots and [] for arrays, e.g. data.items[].price. Standard library only.
"""
import argparse
import difflib
import json
import re
import sys
from urllib.parse import urlparse


def type_name(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "boolean"
    if isinstance(v, (int, float)):
        return "number"
    if isinstance(v, str):
        return "string"
    if isinstance(v, list):
        return "array"
    return "object"


def shape(node, path="", out=None):
    """Map every path to the set of types seen there (arrays merged across items)."""
    out = {} if out is None else out
    out.setdefault(path or "$", set()).add(type_name(node))
    if isinstance(node, dict):
        for k, v in node.items():
            shape(v, f"{path}.{k}" if path else k, out)
    elif isinstance(node, list):
        for item in node:
            shape(item, f"{path}[]", out)
    return out


def diff_shapes(old, new):
    changes = []
    for p in sorted(set(old) - set(new)):
        changes.append({"path": p, "change": "removed", "old": sorted(old[p]), "new": None, "class": "breaking"})
    for p in sorted(set(new) - set(old)):
        changes.append({"path": p, "change": "added", "old": None, "new": sorted(new[p]), "class": "safe"})
    for p in sorted(set(old) & set(new)):
        o, n = old[p], new[p]
        if o == n:
            continue
        if n == {"null"}:
            cls, what = "risky", "null in new sample (nullable?)"
        elif n - o == {"null"} and o - n == set():
            cls, what = "risky", "now nullable"
        elif o - n == {"null"} and n - o == set():
            cls, what = "safe", "no longer null"
        else:
            cls, what = "breaking", "type changed"
        changes.append({"path": p, "change": what, "old": sorted(o), "new": sorted(n), "class": cls})
    # possible renames: removed + added leaf with same types and similar last segment
    def tokens(path):
        leaf = path.split(".")[-1].replace("[]", "")
        return set(t.lower() for t in re.findall(r"[A-Z]?[a-z0-9]+|[A-Z]+(?![a-z])", leaf.replace("_", " ")))

    removed = [c for c in changes if c["change"] == "removed"]
    added = [c for c in changes if c["change"] == "added"]
    renames = []
    for r in removed:
        leaf = r["path"].split(".")[-1].replace("[]", "").replace("_", "").lower()
        best, score = None, 0.0
        for a in added:
            if a["new"] != r["old"]:
                continue
            cand = a["path"].split(".")[-1].replace("[]", "").replace("_", "").lower()
            t_old, t_new = tokens(r["path"]), tokens(a["path"])
            jaccard = len(t_old & t_new) / len(t_old | t_new) if (t_old | t_new) else 0.0
            s = max(difflib.SequenceMatcher(None, leaf, cand).ratio(), jaccard)
            if s > score:
                best, score = a, s
        if best and score >= 0.6:
            renames.append({"old": r["path"], "new": best["path"], "similarity": round(score, 2)})
    order = {"breaking": 0, "risky": 1, "safe": 2}
    changes.sort(key=lambda c: (order[c["class"]], c["path"]))
    return changes, renames


def load(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "log" in data and "entries" in data.get("log", {}):
        bodies = {}
        for e in data["log"]["entries"]:
            req, content = e.get("request", {}), e.get("response", {}).get("content", {})
            text = content.get("text")
            if not text or "json" not in content.get("mimeType", ""):
                continue
            try:
                key = f"{req.get('method', 'GET')} {urlparse(req.get('url', '')).path}"
                bodies.setdefault(key, json.loads(text))
            except (ValueError, TypeError):
                continue
        return bodies, True
    return data, False


def report(name, changes, renames):
    lines = [f"## {name}"]
    if not changes:
        return "\n".join(lines + ["No shape changes.", ""])
    verdict = "Breaking" if any(c["class"] == "breaking" for c in changes) else (
        "Risky" if any(c["class"] == "risky" for c in changes) else "Safe")
    lines.append(f"Verdict: {verdict}")
    lines.append("| Path | Change | Old | New | Class |")
    lines.append("|---|---|---|---|---|")
    for c in changes:
        fmt = lambda t: "-" if t is None else "/".join(t)
        lines.append(f"| {c['path']} | {c['change']} | {fmt(c['old'])} | {fmt(c['new'])} | {c['class']} |")
    if renames:
        lines.append("Possible renames (breaking for old clients):")
        lines += [f"- {r['old']} -> {r['new']} (similarity {r['similarity']})" for r in renames]
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    old, old_har = load(a.old)
    new, new_har = load(a.new)
    results = {}
    if old_har and new_har:
        for key in sorted(set(old) | set(new)):
            if key not in new:
                results[key] = ([{"path": "$", "change": "endpoint removed", "old": ["present"], "new": None, "class": "breaking"}], [])
            elif key not in old:
                results[key] = ([{"path": "$", "change": "endpoint added", "old": None, "new": ["present"], "class": "safe"}], [])
            else:
                results[key] = diff_shapes(shape(old[key]), shape(new[key]))
    else:
        results["response"] = diff_shapes(shape(old), shape(new))
    if a.json:
        print(json.dumps({k: {"changes": c, "renames": r} for k, (c, r) in results.items()}, indent=2))
    else:
        print("\n".join(report(k, c, r) for k, (c, r) in results.items()))
    sys.exit(1 if any(c["class"] == "breaking" for cs, _ in results.values() for c in cs) else 0)


if __name__ == "__main__":
    main()
