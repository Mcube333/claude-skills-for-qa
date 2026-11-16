---
name: test-execution-reporter
description: Turn raw test execution results - a test case sheet with pass/fail columns, automation reports (Allure, TestNG, JUnit XML, Playwright, Surefire), CI run output, or plain notes - into a clear stakeholder report and a release go/no-go recommendation, plus ready-to-post Slack/Teams sign-off and email versions. Calculates pass rates per area, platform and variant, lists blockers by severity, separates product bugs from test or environment failures, and states residual risk. Use this whenever the user says "summarise the test run", "QA sign-off", "release readiness", "test summary report", "share results with PM", "are we good to release", or pastes results and wants something to send - even if they don't say "report".
---

# Test Execution Reporter

People reading a test report want three answers fast: can we release, what is still broken, and what
is the risk if we go ahead. Detail is for those who ask. This skill leads with the decision and keeps
the numbers honest.

## Workflow

1. **Parse the results.** Count per status: Passed, Failed, Blocked, Skipped/Not run, and (for
   automation) Flaky / passed on retry. Break down by whatever dimensions exist: feature area,
   platform, variant, priority, suite. Never drop "not run" from the denominator silently; report
   pass rate both of executed and of planned.
2. **Classify failures.** For each failed or blocked case, decide: product bug (link the ticket if
   known), test/script issue, environment/data issue, or unknown. Only product bugs count against
   release quality, but the others must be listed because they reduce real coverage.
3. **List blockers.** Open defects found by this run, by severity/priority, with status (open, fixed,
   in retest, deferred with approval).
4. **Decide.** Recommend one of: **Go**, **Go with known issues** (list them and who accepted them),
   or **No-go** (list what must be fixed and retested). Use the rules in `references/go-no-go.md`.
   The user or their lead makes the final call; the recommendation must show its reasoning.
5. **Write the outputs** below. Match the user's audience: PM/stakeholder version short, QA/dev
   version with full tables.

## Output

### 1. Report (default)

```
## Test execution report: <feature / release> | <env> | <date range>

Recommendation: <Go / Go with known issues / No-go> - <one-line reason>

| Planned | Executed | Passed | Failed | Blocked | Not run | Pass rate (executed) | Pass rate (planned) |

By area / platform:
| Area | Platform | Executed | Passed | Failed | Blocked | Pass % |

Open defects:
| ID | Title | Severity | Priority | Status | Owner |

Failures not caused by product bugs: <n test issues, n environment issues, with one line each>
Not covered: <what was not tested and why>
Residual risk: <2-3 lines>
Next steps: <retest, fixes needed, owners, dates>
```

### 2. Slack / Teams sign-off (always offer)

Short, scannable, no tables (chat apps render them badly):

```
QA update - <feature> (<env>)
Status: <Go / Go with known issues / No-go>
Executed <x>/<planned> | Passed <p> | Failed <f> | Blocked <b>
Blockers: <ID - one line> (or "none")
Known issues accepted: <ID - one line> (or "none")
Not tested: <one line>
Report: <link>
```

### 3. Email version (on request)
Subject line with status, then the recommendation paragraph, the summary numbers, blockers and a link.

## Rules

- Numbers must add up; recheck totals before writing.
- Do not call a release "Go" with open Critical/P1 product bugs unless the user says a named person accepted them.
- Flaky passes are reported as passes but counted and named, because they hide risk.
- Keep customer data, credentials and internal hostnames out of anything meant for wide channels.
