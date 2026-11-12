#!/usr/bin/env python3
"""Flakiness stats across multiple test runs.

Usage:
  python flake_stats.py run1/ run2/ results/*.xml [--min-runs 2] [--all]

Accepts JUnit/Surefire XML (TEST-*.xml, junitreport) and TestNG (testng-results.xml),
files or directories (searched recursively for *.xml). Each file (or each directory passed
as an argument) is treated as one run unless --per-file is given.

Prints per test: runs, passes, fails, skips, pass rate, flips (outcome changes between
consecutive runs), and failure messages grouped by a normalized signature (numbers, ids,
hex, uuids, quoted values collapsed) so the same root cause groups together.
"""
import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict, Counter


def iter_xml(path):
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for f in sorted(files):
                if f.endswith(".xml"):
                    yield os.path.join(root, f)
    elif path.endswith(".xml"):
        yield path


NORMALIZERS = [
    (re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I), "<uuid>"),
    (re.compile(r"0x[0-9a-f]+", re.I), "<hex>"),
    (re.compile(r"(Bearer|token[=:])\s*\S+", re.I), r"\1 <redacted>"),
    # quoted values are kept: they often carry the real error text ("Target page ... closed")
    (re.compile(r"\d+(\.\d+)?"), "<n>"),
    (re.compile(r"\s+"), " "),
]


def signature(msg):
    first = (msg or "").strip().splitlines()[0] if msg and msg.strip() else "(no message)"
    s = first[:300]
    for rx, rep in NORMALIZERS:
        s = rx.sub(rep, s)
    return s.strip()[:180]


def parse_junit(root):
    for tc in root.iter("testcase"):
        name = f"{tc.get('classname', '')}.{tc.get('name', '')}".strip(".")
        status, msg = "pass", None
        for tag in ("failure", "error"):
            el = tc.find(tag)
            if el is not None:
                status = "fail"
                msg = el.get("message") or (el.text or "")
                break
        if status == "pass" and tc.find("skipped") is not None:
            status = "skip"
        yield name, status, msg


def parse_testng(root):
    for cls in root.iter("class"):
        cname = cls.get("name", "")
        for m in cls.iter("test-method"):
            if m.get("is-config") == "true":
                continue
            name = f"{cname}.{m.get('name', '')}"
            params = [p.findtext("value", "").strip() for p in m.iter("param")]
            if params:
                name += "[" + ",".join(x[:30] for x in params) + "]"
            st = m.get("status", "").upper()
            status = {"PASS": "pass", "FAIL": "fail", "SKIP": "skip"}.get(st, "skip")
            msg = None
            if status == "fail":
                exc = m.find("exception")
                if exc is not None:
                    msg = (exc.findtext("message") or exc.get("class") or "").strip() or exc.get("class")
            yield name, status, msg


def parse_file(path):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return []
    if root.tag == "testng-results":
        return list(parse_testng(root))
    if root.tag in ("testsuite", "testsuites"):
        return list(parse_junit(root))
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--min-runs", type=int, default=2)
    ap.add_argument("--per-file", action="store_true", help="treat every XML file as its own run")
    ap.add_argument("--all", action="store_true", help="also list stable tests")
    args = ap.parse_args()

    runs = []  # list of dict test -> (status, msg)
    for p in args.paths:
        files = list(iter_xml(p))
        if not files:
            continue
        if os.path.isdir(p) and not args.per_file:
            run = {}
            for f in files:
                for name, st, msg in parse_file(f):
                    run[name] = (st, msg)
            if run:
                runs.append(run)
        else:
            for f in files:
                run = {name: (st, msg) for name, st, msg in parse_file(f)}
                if run:
                    runs.append(run)

    if not runs:
        sys.exit("No test results found.")

    history = defaultdict(list)
    for run in runs:
        for name, res in run.items():
            history[name].append(res)

    rows = []
    for name, res in history.items():
        statuses = [s for s, _ in res if s != "skip"]
        if len(statuses) < args.min_runs:
            continue
        passes, fails = statuses.count("pass"), statuses.count("fail")
        flips = sum(1 for a, b in zip(statuses, statuses[1:]) if a != b)
        sigs = Counter(signature(m) for s, m in res if s == "fail")
        skips = sum(1 for s, _ in res if s == "skip")
        rows.append((name, len(statuses), passes, fails, skips, flips, sigs))

    flaky = [r for r in rows if r[2] > 0 and r[3] > 0]
    always_fail = [r for r in rows if r[2] == 0 and r[3] > 0]
    stable = [r for r in rows if r[3] == 0]

    print(f"# Flake stats: {len(runs)} run(s), {len(rows)} test(s) with >= {args.min_runs} executed runs\n")
    print(f"flaky={len(flaky)}  always-failing={len(always_fail)}  stable={len(stable)}\n")

    def show(title, items):
        if not items:
            return
        print(f"## {title}")
        print("| Test | Runs | Pass | Fail | Pass rate | Flips |")
        print("|---|---|---|---|---|---|")
        for name, n, p, f, _, flips, _s in items:
            print(f"| {name} | {n} | {p} | {f} | {p / n:.0%} | {flips} |")
        print()
        for name, n, p, f, _, flips, sigs in items:
            if sigs:
                print(f"**{name}** failure signatures:")
                for sig, c in sigs.most_common(5):
                    print(f"  - {c}x {sig}")
        print()

    show("Flaky (mixed pass/fail)", sorted(flaky, key=lambda r: (r[2] / r[1], -r[5])))
    show("Always failing (not flaky: real break or env)", always_fail)
    if args.all:
        show("Stable", stable)


if __name__ == "__main__":
    main()
