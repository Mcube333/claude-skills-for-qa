#!/usr/bin/env python3
"""Build a formatted QA test-case workbook from JSON (see schema.json).

Usage:
  python build_workbook.py cases.json "Feature - Test Cases.xlsx"

Sheets: Summary (live formulas), Test Cases, Findings, Traceability.
Prints validation warnings (duplicate ids, unknown req/finding references, uncovered requirements).
"""
import json
import sys

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

FONT = "Arial"
HEADER_FILL = PatternFill("solid", fgColor="1F3864")
HEADER_FONT = Font(name=FONT, bold=True, color="FFFFFF", size=10)
BODY_FONT = Font(name=FONT, size=10)
BOLD = Font(name=FONT, size=10, bold=True)
TITLE = Font(name=FONT, size=14, bold=True)
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")

PRIORITY_FILL = {
    "P0": "F8CBAD", "P1": "FCE4D6", "P2": "FFF2CC", "P3": "EDEDED",
}
SEVERITY_FILL = {"High": "F8CBAD", "Medium": "FFF2CC", "Low": "E2EFDA"}
STATUS_COLORS = {
    "Pass": "C6EFCE", "Fail": "FFC7CE", "Blocked": "FFEB9C", "Skipped": "D9D9D9", "Not Run": "FFFFFF",
}
STATUSES = ["Not Run", "Pass", "Fail", "Blocked", "Skipped"]
FINDING_TYPES = ["Contradiction", "PRD-Design mismatch", "Gap", "Ambiguity", "Risk"]
SEVERITIES = ["High", "Medium", "Low"]
PRIORITIES = ["P0", "P1", "P2", "P3"]


def as_list(v):
    if v is None or v == "":
        return []
    return v if isinstance(v, list) else [x.strip() for x in str(v).split(",") if x.strip()]


def header(ws, cols, widths):
    for i, (name, w) in enumerate(zip(cols, widths), start=1):
        c = ws.cell(row=1, column=i, value=name)
        c.font, c.fill, c.alignment, c.border = HEADER_FONT, HEADER_FILL, Alignment(wrap_text=True, vertical="center"), BORDER
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[1].height = 30
    ws.freeze_panes = "B2"


def body_cell(ws, r, c, v):
    cell = ws.cell(row=r, column=c, value=v)
    cell.font, cell.alignment, cell.border = BODY_FONT, WRAP, BORDER
    return cell


def validate(data):
    warns = []
    reqs = {r["id"] for r in data.get("requirements", [])}
    finds = {f["id"] for f in data.get("findings", [])}
    seen = set()
    for tc in data["test_cases"]:
        if tc["id"] in seen:
            warns.append(f"Duplicate test case id {tc['id']}")
        seen.add(tc["id"])
        for r in as_list(tc.get("req_ids")):
            if reqs and r not in reqs:
                warns.append(f"{tc['id']} references unknown requirement {r}")
        for f in as_list(tc.get("blocked_by")):
            if f not in finds:
                warns.append(f"{tc['id']} blocked by unknown finding {f}")
        if not tc.get("expected"):
            warns.append(f"{tc['id']} has no expected result")
    covered = {r for tc in data["test_cases"] for r in as_list(tc.get("req_ids"))}
    for r in sorted(reqs - covered):
        warns.append(f"Requirement {r} has no test cases")
    # Cross-check findings <-> cases, then make impacted_cases the union so the workbook is consistent.
    blocked_map = {}
    for tc in data["test_cases"]:
        for fid in as_list(tc.get("blocked_by")):
            blocked_map.setdefault(fid, []).append(tc["id"])
    case_ids = {tc["id"] for tc in data["test_cases"]}
    for f in data.get("findings", []):
        listed = as_list(f.get("impacted_cases"))
        for cid in listed:
            if cid not in case_ids:
                warns.append(f"{f['id']} lists unknown case {cid}")
            elif cid not in blocked_map.get(f["id"], []):
                warns.append(f"{f['id']} lists {cid}, but {cid} is not blocked by {f['id']} (wrong id or missing blocked_by)")
        merged = [c for c in listed if c in case_ids]
        merged += [c for c in blocked_map.get(f["id"], []) if c not in merged]
        f["impacted_cases"] = merged
    for f in data.get("findings", []):
        if f.get("severity") == "High" and not as_list(f.get("impacted_cases")):
            warns.append(f"High finding {f['id']} lists no impacted cases (add them or note 'no test impact')")
    return warns


def build(data, out):
    wb = Workbook()
    summary = wb.active
    summary.title = "Summary"
    tc_ws = wb.create_sheet("Test Cases")
    f_ws = wb.create_sheet("Findings")
    t_ws = wb.create_sheet("Traceability")

    cases = data["test_cases"]
    findings = data.get("findings", [])
    reqs = data.get("requirements", [])
    meta = data.get("meta", {})

    # ---------------- Test Cases ----------------
    cols = ["ID", "Module", "Title", "Req IDs", "Type", "Priority", "Platforms", "Preconditions",
            "Test Data", "Steps", "Expected Result", "Automation", "Blocked by", "Status",
            "Actual Result", "Bug ID", "Notes"]
    widths = [9, 14, 40, 14, 12, 9, 18, 28, 24, 48, 48, 14, 12, 11, 30, 12, 28]
    header(tc_ws, cols, widths)
    tc_ws.freeze_panes = "D2"
    for r, tc in enumerate(cases, start=2):
        steps = as_list(tc.get("steps")) if isinstance(tc.get("steps"), list) else [tc.get("steps", "")]
        blocked = as_list(tc.get("blocked_by"))
        vals = [
            tc["id"], tc.get("module", ""), tc.get("title", ""), ", ".join(as_list(tc.get("req_ids"))),
            tc.get("type", ""), tc.get("priority", ""), ", ".join(as_list(tc.get("platforms"))),
            tc.get("preconditions", ""), tc.get("test_data", ""),
            "\n".join(f"{i}. {s}" for i, s in enumerate(steps, start=1) if s),
            tc.get("expected", ""), tc.get("automation", ""), ", ".join(blocked),
            # Only truly undefined expectations start Blocked; "assumed, confirm F-x" cases are runnable.
            tc.get("status") or ("Blocked" if blocked and "TBD" in str(tc.get("expected", "")) else "Not Run"),
            "", "", tc.get("notes", ""),
        ]
        for c, v in enumerate(vals, start=1):
            body_cell(tc_ws, r, c, v)
        pr = tc.get("priority", "")
        if pr in PRIORITY_FILL:
            tc_ws.cell(row=r, column=6).fill = PatternFill("solid", fgColor=PRIORITY_FILL[pr])
            tc_ws.cell(row=r, column=6).font = BOLD
    last_tc = max(len(cases) + 1, 2)
    tc_ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{last_tc}"
    dv = DataValidation(type="list", formula1='"' + ",".join(STATUSES) + '"', allow_blank=False)
    tc_ws.add_data_validation(dv)
    dv.add(f"N2:N{last_tc + 200}")  # room for added rows
    for st, color in STATUS_COLORS.items():
        tc_ws.conditional_formatting.add(
            f"N2:N{last_tc + 200}",
            CellIsRule(operator="equal", formula=[f'"{st}"'], fill=PatternFill("solid", fgColor=color)))

    # ---------------- Findings ----------------
    fcols = ["ID", "Type", "Severity", "Source", "Description", "Question", "Owner",
             "Impacted Cases", "Status", "Answer / Resolution"]
    fwidths = [8, 20, 10, 28, 50, 45, 10, 16, 11, 40]
    header(f_ws, fcols, fwidths)
    for r, f in enumerate(findings, start=2):
        vals = [f["id"], f.get("type", ""), f.get("severity", ""), f.get("source", ""),
                f.get("description", ""), f.get("question", ""), f.get("owner", ""),
                ", ".join(as_list(f.get("impacted_cases"))), f.get("status", "Open"), f.get("answer", "")]
        for c, v in enumerate(vals, start=1):
            body_cell(f_ws, r, c, v)
        sev = f.get("severity", "")
        if sev in SEVERITY_FILL:
            f_ws.cell(row=r, column=3).fill = PatternFill("solid", fgColor=SEVERITY_FILL[sev])
            f_ws.cell(row=r, column=3).font = BOLD
    last_f = max(len(findings) + 1, 2)
    f_ws.auto_filter.ref = f"A1:J{last_f}"
    fdv = DataValidation(type="list", formula1='"Open,Answered,Closed"')
    f_ws.add_data_validation(fdv)
    fdv.add(f"I2:I{last_f + 100}")

    # ---------------- Traceability ----------------
    tcols = ["Req ID", "Source", "Requirement", "# Cases", "Case IDs", "Implicit"]
    header(t_ws, tcols, [10, 22, 60, 9, 40, 9])
    case_rng = f"'Test Cases'!$D$2:$D${last_tc}"
    for r, req in enumerate(reqs, start=2):
        ids = [tc["id"] for tc in cases if req["id"] in as_list(tc.get("req_ids"))]
        body_cell(t_ws, r, 1, req["id"])
        body_cell(t_ws, r, 2, req.get("source", ""))
        body_cell(t_ws, r, 3, req.get("text", ""))
        # Exact-token match on the comma-separated Req IDs column (REQ-1 never matches REQ-10)
        body_cell(t_ws, r, 4, f'=SUMPRODUCT(--ISNUMBER(SEARCH(", "&A{r}&",",", "&{case_rng}&",")))')
        body_cell(t_ws, r, 5, ", ".join(ids))
        body_cell(t_ws, r, 6, "Yes" if req.get("implicit") else "")
    last_r = max(len(reqs) + 1, 2)
    t_ws.auto_filter.ref = f"A1:F{last_r}"
    t_ws.conditional_formatting.add(
        f"A2:F{last_r}",
        FormulaRule(formula=[f"$D2=0"], fill=PatternFill("solid", fgColor="FFC7CE")))
    note_r = last_r + 2
    body_cell(t_ws, note_r, 1, "Note").font = BOLD
    t_ws.cell(row=note_r, column=3, value="'# Cases' is a live formula over Test Cases; 'Case IDs' is a snapshot from generation time.").font = BODY_FONT

    # ---------------- Summary ----------------
    s = summary
    s.column_dimensions["A"].width = 26
    s.column_dimensions["B"].width = 14
    s.column_dimensions["C"].width = 4
    s.column_dimensions["D"].width = 24
    s.column_dimensions["E"].width = 14
    s["A1"] = f"{meta.get('feature', 'Feature')} - Test Suite"
    s["A1"].font = TITLE
    row = 3
    for label, key in (("Version / sources", "version"), ("Author", "author")):
        if meta.get(key):
            s.cell(row=row, column=1, value=label).font = BOLD
            s.cell(row=row, column=2, value=meta[key]).font = BODY_FONT
            row += 1
    if meta.get("sources"):
        s.cell(row=row, column=1, value="Sources").font = BOLD
        s.cell(row=row, column=2, value="; ".join(meta["sources"])).font = BODY_FONT
        row += 1
    if meta.get("notes"):
        s.cell(row=row, column=1, value="Notes").font = BOLD
        s.cell(row=row, column=2, value=meta["notes"]).font = BODY_FONT
        row += 1
    row += 1

    tc_col = lambda letter: f"'Test Cases'!${letter}$2:${letter}${last_tc}"

    def table(r0, c0, title, rows):
        """rows: list of (label, formula). Writes a 2-col block; returns next free row."""
        h1 = s.cell(row=r0, column=c0, value=title)
        h2 = s.cell(row=r0, column=c0 + 1, value="Count")
        for h in (h1, h2):
            h.font, h.fill, h.border = HEADER_FONT, HEADER_FILL, BORDER
        r = r0 + 1
        for label, formula in rows:
            a = s.cell(row=r, column=c0, value=label)
            b = s.cell(row=r, column=c0 + 1, value=formula)
            for cell in (a, b):
                cell.font, cell.border = BODY_FONT, BORDER
            r += 1
        return r

    top = row
    # Left column of tables
    pri_rows = [(p, f'=COUNTIF({tc_col("F")},"{p}")') for p in PRIORITIES]
    pri_rows.append(("Total", f"=COUNTA({tc_col('A')})"))
    r = table(top, 1, "Cases by priority", pri_rows)
    s.cell(row=r - 1, column=1).font = BOLD
    s.cell(row=r - 1, column=2).font = BOLD

    types = sorted({tc.get("type", "") for tc in cases if tc.get("type")})
    r = table(r + 1, 1, "Cases by type", [(t, f'=COUNTIF({tc_col("E")},"{t}")') for t in types])

    plats = meta.get("platforms") or sorted({p for tc in cases for p in as_list(tc.get("platforms"))})
    r = table(r + 1, 1, "Cases by platform", [
        (p, f'=SUMPRODUCT(--ISNUMBER(SEARCH(", {p},",", "&{tc_col("G")}&",")))') for p in plats])

    r = table(r + 1, 1, "Automation", [
        ("Yes", f'=COUNTIF({tc_col("L")},"Yes*")'),
        ("Later", f'=COUNTIF({tc_col("L")},"Later*")'),
        ("No", f'=COUNTIF({tc_col("L")},"No*")'),
    ])

    # Right column of tables
    st_range = f"'Test Cases'!$N$2:$N${last_tc + 200}"
    r2 = table(top, 4, "Execution status", [(st, f'=COUNTIF({st_range},"{st}")') for st in STATUSES])
    pr_row = r2
    s.cell(row=pr_row, column=4, value="Pass rate (executed)").font = BOLD
    first_status = top + 1
    pass_cell = f"E{first_status + STATUSES.index('Pass')}"
    fail_cell = f"E{first_status + STATUSES.index('Fail')}"
    c = s.cell(row=pr_row, column=5, value=f"=IFERROR({pass_cell}/({pass_cell}+{fail_cell}),\"-\")")
    c.number_format = "0%"
    c.font = BOLD
    r2 = pr_row + 2

    f_rng = lambda letter: f"Findings!${letter}$2:${letter}${last_f + 100}"
    r2 = table(r2, 4, "Findings by type", [(t, f'=COUNTIF({f_rng("B")},"{t}")') for t in FINDING_TYPES])
    r2 = table(r2 + 1, 4, "Findings by severity", [(sv, f'=COUNTIF({f_rng("C")},"{sv}")') for sv in SEVERITIES]
               + [("Open", f'=COUNTIF({f_rng("I")},"Open")')])

    cov_r = r2 + 1
    s.cell(row=cov_r, column=4, value="Requirement coverage").font = BOLD
    cov = s.cell(row=cov_r, column=5,
                 value=f"=IFERROR(COUNTIF(Traceability!$D$2:$D${last_r},\">0\")/COUNTA(Traceability!$A$2:$A${last_r}),\"-\")")
    cov.number_format = "0%"
    cov.font = BOLD
    s.cell(row=cov_r + 1, column=4, value="Uncovered requirements").font = BOLD
    s.cell(row=cov_r + 1, column=5, value=f"=COUNTIF(Traceability!$D$2:$D${last_r},0)").font = BOLD

    for ws in (s, tc_ws, f_ws, t_ws):
        ws.sheet_view.zoomScale = 100
    wb.save(out)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    with open(sys.argv[1], encoding="utf-8") as fh:
        data = json.load(fh)
    if not data.get("test_cases"):
        sys.exit("JSON has no test_cases")
    warns = validate(data)
    build(data, sys.argv[2])
    print(f"Wrote {sys.argv[2]}: {len(data['test_cases'])} cases, {len(data.get('findings', []))} findings, "
          f"{len(data.get('requirements', []))} requirements")
    if warns:
        print("Warnings:")
        for w in warns:
            print(f"  - {w}")


if __name__ == "__main__":
    main()
