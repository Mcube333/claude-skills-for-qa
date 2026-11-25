# Evidence and reporting

## Statuses

| Status | Meaning |
|---|---|
| PASS | Expected behaviour directly verified with sufficient evidence |
| FAIL | Observed behaviour contradicts expected, reproducible, evidenced |
| BLOCKED | Could not execute: env, access, dependency or data blocker (say which) |
| NOT_RUN | Not executed (say why) |
| INCONCLUSIVE | Evidence ambiguous or insufficient |
| NOT_APPLICABLE | Scenario does not apply (say why) |

Map to the team's tool statuses only when writing to that tool.

## Claim labels

FACT (directly observed, with source) · HYPOTHESIS (plausible, unproven) · ASSUMPTION
(taken as true to proceed) · RECOMMENDATION (suggested action).

## Result row

| ID | Scenario | Env / platform / build | Variant | Expected | Observed | Status | Evidence |
|---|---|---|---|---|---|---|---|

Evidence column: screenshot name, request id, trace id, Sentry issue, query + row count,
event name + timestamp. No secrets or raw PII.

## Triage note

```
Summary: <one line>
Verdict: Product bug | Test issue | Env | Config/flag | Third party | Cannot reproduce
Env / build / platform / variant:
Repro steps:
Expected / Actual:
Evidence:
  FACT: ...
  FACT: ...
Hypotheses (ranked):
  H1: ... (supports / against)
Next diagnostic step:
Recommended owner / severity:
```

## Bug draft

```
Title: [Platform][Area] <observable problem>
Environment: <env, build/app version, device/OS/browser>
Preconditions: <account role, flag/variant, data state>
Steps to reproduce:
1.
Expected result:
Actual result:
Evidence: <screenshots, request ids, logs, query>
Frequency: <always / n of m>
Severity / priority: <proposed>
Links: <story, epic, related defects>
```
Apply the team's Jira conventions (project, issue type, component, labels, epic link,
assignee) when known. Show the draft; file only after approval.

## Regression scope

```
Change: <PR / release>
Must-run smoke: <cases + reason>
Focused regression: <cases + reason>
Full regression recommended?: yes/no + reason
Not affected: <areas + reason>
Risks / unknowns:
```

## Release sign-off

```
Release: <name, build, commit>   Env: <env>   Date:
Platforms: <web/mweb/Android/iOS + versions>
Execution: PASS n · FAIL n · BLOCKED n · NOT_RUN n · INCONCLUSIVE n
Open defects: <id, severity, status, workaround>
Blocked / not-run coverage: <what and why>
Flags / rollout plan:
CI status / telemetry signals:
Risks:
Recommendation: GO | GO WITH RISKS | NO-GO  (human decision pending)
```
