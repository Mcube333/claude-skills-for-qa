---
name: analytics-event-auditor
description: Audit product analytics / event tracking against a tracking spec, for any tool (MoEngage, Amplitude, Mixpanel, Segment, GA4, CleverTap, Firebase, WebEngage, custom). Finds missing and unexpected events, naming mismatches, missing/extra/mistyped attributes, invalid enum values, duplicate fires, wrong order, environment/workspace mismatches, and PII leaking into event or user attributes. Works from a spec sheet plus captured events (tool export CSV/JSON, HAR/network capture, proxy logs, debug-view copy). Use this whenever the user wants to "audit tracking", "verify events", "check analytics for this feature", "QA the tracking plan", compares events against a spec or tracking sheet, shares a HAR or event export and asks what's wrong, or asks whether events contain PII, even if they don't name a specific tool.
---

# Analytics Event Auditor

Tracking bugs are silent: nothing crashes, the dashboard is just wrong for weeks. This skill checks captured events against the spec mechanically (so nothing is eyeballed), then adds the judgement a script can't make (was it fired at the right moment, is a missing attribute a bug or a spec issue).

## 1. Get the spec

Accepted: CSV/XLSX/Google Sheet/Confluence table/pasted table. Normalize to one row per attribute using the columns in `assets/spec_template.csv`:

`event, trigger, platforms, attribute, type, required, allowed_values, notes`

- Event-only rows (no attribute) are fine.
- `type`: string, int, number, bool, datetime, array, object.
- `allowed_values`: `|`-separated enum.
- If the spec is missing types or required flags, assume `string` / `required=yes` and say so in the report. Don't invent attributes the spec doesn't list.

Spec problems are findings too: the same event spelled two ways, attributes with PII by design (e.g. `user_phone` as a planned attribute), inconsistent naming styles. Report them in a "Spec issues" section.

## 2. Get the captured events

Prefer, in order: what the user provides → a connected analytics connector/MCP (if available and working) → the tool's UI via a browser tool (user activity/event stream for a test user) → a HAR/network capture of the SDK calls.

If one route fails (e.g. API returns 401/403), say so in one line and switch to the next route instead of stopping.

Know which **environment/workspace** the events should be in (test vs production project, app id, API key, data center) and pass it to the script with `--expect`, because events landing in the wrong workspace is a common and easily missed bug.

Mask PII when quoting events anywhere in the reply (the script already masks values in its output).

## 3. Run the audit

```bash
python scripts/audit_events.py --spec spec.csv --events capture.har [more files...] \
    [--platform android] [--expect app_id=TEST_123] [--flow "cart_viewed,coupon_applied,checkout_started"] \
    [--dup-window 2] [--hosts "api.mixpanel.com,moengage"] [--xlsx audit.xlsx] [--json audit.json]
```

Inputs it understands: HAR (extracts analytics requests: JSON, form-encoded, base64 batches, GA4 query params), JSON exports (Segment, Amplitude, Mixpanel, generic arrays), CSV exports (an event-name column plus attribute columns or a JSON properties column). See `references/payload-formats.md` if a format isn't picked up; `--name-key` and `--attr-key` override the field names.

It reports: spec coverage per event (found / missing / name mismatch), attribute issues (missing required, extra, wrong type, value not in enum, empty/null), PII hits (by key name and by value pattern, with masked samples), duplicate fires within the window, out-of-order flow, expectation mismatches (`--expect`), unexpected events not in the spec, and casing/style inconsistencies.

## 4. Review what the script can't judge

- **Trigger timing**: compare event timestamps with the test steps (e.g. `order_placed` must fire on payment success, not on tapping Pay). Needs the user's action log or test steps.
- **Values correctness**: `cart_value` present and numeric isn't enough; check it equals what the UI showed.
- **Missing vs not exercised**: an event can be "missing" because the test session never triggered it. Mark these "not exercised" if the steps didn't cover the trigger.
- **Rename vs new event**: a near-match name (`couponApplied` vs `coupon_applied`) is usually the same event shipped under a different name. Report it as a naming mismatch, not as one missing + one unexpected.
- **Per-platform differences**: run per platform (`--platform`) or compare platforms side by side; differences across iOS/Android/web for the same event are common.
- **Flat CSV exports lose types**: the script coerces values and adds a note; don't report type issues from a CSV as confirmed. Ask for a HAR/proxy capture when types matter.
- **PII false positives**: value-only hits on id-like keys (`order_id`) are marked "likely false positive"; say so explicitly rather than dropping or escalating them.
- **Volumes**: if dashboard access exists, a 30-day count per platform per event quickly shows platforms where an event never fires. Zero on one platform and thousands on another = platform-specific bug.

## 5. Report

Lead with a short summary: events checked, % of spec events found, counts by severity. Then sections, each issue with **severity**, evidence (masked), and the fix owner:

| Severity | Use for |
|---|---|
| Critical | PII in events; events going to the wrong workspace/environment; revenue/order events missing or duplicated |
| High | Spec event missing/never fires on a platform; required attribute missing; wrong type that breaks reports; naming mismatch on key funnel events |
| Medium | Enum violations; duplicates on non-revenue events; extra undocumented attributes; out-of-order flow |
| Low | Casing/style inconsistencies; optional attribute missing |

Offer, in one line, to turn Critical/High issues into bug tickets (title, steps, expected vs actual, evidence) if a tracker connector is available or the user wants text to paste. Produce an .xlsx only if the user asks for a file (`--xlsx`).

## Bundled files

- `scripts/audit_events.py`: the audit engine (stdlib only; openpyxl only for `--xlsx`).
- `assets/spec_template.csv`: spec format with examples.
- `references/payload-formats.md`: how events are extracted from common SDK payloads and exports; override flags.
- `references/pii-rules.md`: what counts as PII here, detection patterns, and masking rules.
