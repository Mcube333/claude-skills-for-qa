---
name: prd-to-test-cases
description: Turn a PRD, spec, user stories, or design (Figma frames/screenshots) into a reviewed manual test suite - first surfacing contradictions, PRD-vs-design mismatches, gaps and open questions, then writing traceable, prioritized test cases (positive, negative, boundary, state, platform, A/B variant, analytics) and delivering them as a multi-sheet Excel workbook (Summary, Test Cases, Findings, Traceability) or in chat. Use this whenever the user shares a PRD/requirements doc, a feature spec, acceptance criteria, Jira epic/story text, or design screens and asks for test cases, a test plan, test scenarios, "what should I test", "QA review of this PRD", or "find gaps in this spec", even if they don't say "test cases" explicitly.
---

# PRD → Test Cases

A good QA pass on a PRD finds problems **before** writing tests: the questions and contradictions are often worth more than the cases. So this skill always runs an analysis pass first, then writes cases that trace back to requirements and are honest about what's still undefined.

## 1. Read everything and build a requirement inventory

Sources can be: PRD, user stories/acceptance criteria, Figma frames or screenshots, API specs, analytics/tracking specs, existing test cases. If a Figma or Drive/Confluence/Jira connector is available and the user linked a file, read it through the connector.

Split the material into atomic, testable requirements: `REQ-01 … REQ-nn`, each with a **source reference** (PRD section/heading, page, Figma frame name, story ID) and the requirement in one sentence. Atomic means one checkable behaviour: "Coupon field accepts alphanumeric codes up to 12 chars and shows an inline error for invalid codes" is two or three requirements.

Include implicit requirements the feature obviously needs even if the PRD is silent (loading, empty and error states, back navigation, session expiry, double-tap/double-submit, offline on mobile), but mark them `(implicit)` so it's clear they're QA-derived.

## 2. Analysis pass: findings

Before writing any test case, go through the inventory and the designs and log findings. Read `references/review-checklist.md` for what to look for. Each finding has:

| Field | Content |
|---|---|
| ID | `F-01…` |
| Type | `Contradiction` (PRD vs itself) · `PRD-Design mismatch` · `Gap` (behaviour undefined) · `Ambiguity` (defined but open to two readings) · `Risk` (defined, but likely to break something: performance, data migration, existing flows) |
| Severity | `High` (blocks testing or likely user-facing defect) · `Medium` · `Low` (cosmetic/wording) |
| Source | exact references on both sides for contradictions/mismatches (e.g. "PRD §4.2 vs Figma 'Cart – coupon applied'") |
| Description | what conflicts or is missing, concretely |
| Question | the question to ask, phrased so it can be answered in one line |
| Owner | PM / Design / Dev / Analytics (best guess) |
| Impacted cases | test case IDs that depend on the answer |

Don't invent the answer to an open question. Cases that depend on it list the finding in `Blocked by` and either:
- state the most likely behaviour **marked "(assumed, confirm F-07)"**: the case is still runnable and starts as *Not Run*; or
- say "TBD per F-07" when there's no reasonable default: the case starts as *Blocked*.

`impacted_cases` on a finding is derived from the cases' `Blocked by`, so set `Blocked by` on the cases and the builder fills and cross-checks the finding side; fix any mismatch warnings it prints.

## 3. Design the test cases

Read `references/test-design-techniques.md` for the techniques and the priority rubric. Per requirement, choose the techniques that apply, rather than applying all of them:

- Positive flow(s); negative inputs; boundary values (just inside/at/just outside each limit); equivalence classes for inputs.
- **State transitions** for anything with states (cart, order, subscription, KYC): valid and invalid transitions.
- **Decision tables** when rules combine (coupon × membership × payment method).
- **Platform matrix**: iOS / Android / mobile web / desktop web. Write one case and list platforms, unless behaviour differs per platform; then split.
- **A/B experiments & feature flags**: cases per variant where behaviour differs, plus a case that bucketing is sticky.
- **Analytics/tracking**: event fires once, at the right moment, with the specified attributes and no PII; if a tracking spec is given.
- **Non-functional basics** where relevant: accessibility (labels, focus order, contrast on new components), localization/currency/number formats, interruptions on mobile (background/foreground, call, rotation, permission revoke), slow network.
- **Regression**: existing flows the change touches.

Case count is driven by risk and coverage, not a target number. No duplicates: if two cases differ only in data, make one case with a data table in Test Data.

### Case fields

`ID (TC-001…) · Module · Title · Req IDs · Type · Priority (P0–P3) · Platforms · Preconditions · Test Data · Steps (numbered) · Expected Result · Automation (Yes / No / Later + one-word reason) · Blocked by · Notes`

Quality bar:
- Title says behaviour + condition: "Apply valid coupon below min cart value shows min-value error", not "Coupon test 3".
- Steps are atomic actions a new tester could follow; concrete data, not "enter valid data".
- Expected results are observable (exact message, value, state, event) and placed against the step they verify when there are several.
- No "verify it works correctly". If you can't state the expected result, it's a finding.

## 4. Traceability and self-check

Map every requirement to its cases. Before delivering:
- Every REQ has ≥1 case, or is listed as uncovered with a reason.
- Every High finding is referenced by at least one case or explicitly noted as "no test impact".
- P0 cases cover the main happy path end-to-end on every in-scope platform.

## 5. Deliver

**Workbook** (default when the user asks for Excel/a sheet/a workbook, or when there are more than ~20 cases): write the data as JSON matching `scripts/schema.json`, then run:

```bash
python scripts/build_workbook.py cases.json "<Feature> - Test Cases.xlsx"
```

It produces Summary (counts by priority/type/platform/status and findings by type/severity, all as live formulas; coverage %), Test Cases (frozen header, filters, priority colours, Status dropdown with colour coding for execution), Findings, and Traceability (uncovered requirements highlighted). If an xlsx/spreadsheet skill with a recalculation script is available, read it and run the recalc on the output so formula values are cached for previewers; fix any reported errors.

If the user has an existing workbook format (sheet names, columns, colours), match it instead: edit the JSON → workbook mapping or write the workbook directly following their format.

**In chat** (fewer than ~20 cases, or the user asks for it, or doesn't want files): findings table first, then cases as a compact table (ID, Title, Priority, Steps, Expected), then uncovered requirements.

In either case, the chat reply is short: counts (cases by priority, findings by severity), the top 3–5 High findings in one line each, and anything blocked. Don't restate the workbook.

## Confidentiality

For portfolio/public use, replace company names, internal URLs, real user data, and proprietary event or experiment names with neutral ones and say so in one line.

## Bundled files

- `references/review-checklist.md`: what to look for in a PRD and in designs (states, limits, permissions, copy, analytics, edge cases); common contradiction patterns.
- `references/test-design-techniques.md`: BVA, equivalence partitioning, state transition, decision table, pairwise; priority rubric; examples.
- `scripts/schema.json`: JSON input format for the workbook builder.
- `scripts/build_workbook.py`: JSON → formatted multi-sheet .xlsx (openpyxl).
