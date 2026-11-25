# Workflows

Contents: W1 Requirement → test plan · W2 Change impact · W3 Exploratory/smoke · W4 Defect
triage · W5 API & data · W6 Analytics · W7 Feature flags · W8 CI failure · W9
Non-functional gate · W10 Release sign-off · W11 MCP setup · Orchestration examples

All workflows are read-only until the user approves a specific write.

---

## W1. Requirement → test plan

1. Read the story/epic, acceptance criteria, linked PRD (Confluence/Docs), design links
   and comments. Pull prior defects on the same component (JQL by component/label).
2. If designs are linked and Figma is connected, read the frames: states, empty/error/
   loading variants, copy, tokens.
3. List **gaps**: missing AC, contradictions (PRD vs design vs ticket), undefined error
   states, role/permission assumptions, test-data needs, analytics events, flag/variant.
4. Search existing test cases (test-management tool or prior suites) before writing new
   ones; mark reuse vs new.
5. Write cases with traceability (AC id → case id), priority, platform, variant. Use
   `references/test-design-checklists.md` for the relevant domain.
6. Output: gaps & questions first, then the suite. Offer to create cases/tickets; do not
   create them without approval.

## W2. Change impact & regression scope

1. Read the PR/commits: files changed, components, config/migrations, flags touched.
2. Map changed areas to user journeys and existing test cases.
3. Weight by: business criticality, blast radius (shared components, APIs, DB schema),
   defect history, current error signals (Sentry/Datadog for that area).
4. Output a ranked list: Must-run smoke · Focused regression · Optional/full-regression
   recommendation · Not affected (with reason).

## W3. Exploratory / smoke run

1. Confirm env, base URL, platform, build, test account (role only), flag variant.
2. Bound the session: list the flows and the stop condition (e.g. stop before payment
   submit). Never place real orders, pay, or submit irreversible forms without approval.
3. Drive the browser/device tool step by step. At each checkpoint capture: screenshot,
   console errors, failing network calls (status, endpoint, request id).
4. Record each step's status. Unexpected behaviour → hand to W4.

## W4. Defect triage & RCA

1. **Reproduce** (W3) or take the reporter's evidence. Record exact steps and env.
2. **Client layer**: console errors, failed/slow requests, response bodies (redacted).
3. **Server layer**: find the error by request id/time window in Sentry/Datadog/Grafana;
   note release/version and first-seen.
4. **Data layer**: read-only query for the affected entity (order, user, payment state);
   compare with what UI/API claimed.
5. **Change layer**: recent commits/deploys/flag changes touching the area.
6. **History**: similar Jira defects (summary/component search).
7. Classify: product bug · test/data issue · environment · config/flag · third party ·
   cannot reproduce. Label every statement FACT / HYPOTHESIS / ASSUMPTION.
8. Output a triage note and, if FAIL is confirmed, a bug draft (template in
   `evidence-and-reporting.md`). File only after approval, following the team's Jira
   conventions (project, component, labels, epic link, assignee) if known.

## W5. API & data validation

1. Source the contract: Postman collection/OpenAPI/PR diff.
2. Check: status codes, schema, required/extra fields, types, error contract, auth
   failures, idempotency (repeat same key), retries/timeouts, pagination, versioning.
3. Verify side effects with read-only DB queries: rows created once, correct state,
   timestamps/time zone, currency precision, audit rows.
4. Only call mutating endpoints in a test env with approval; prefer sandbox accounts.

## W6. Analytics & attribution validation

1. Get the tracking spec (event names, attributes, types, enums, platforms).
2. Capture emitted events from the cleanest source available: debug stream, HAR/network,
   the analytics tool's user timeline for a test user (e.g. MoEngage user events).
3. Compare: event existence, fired once, order, attribute names/types/enums, missing/extra
   attributes, identity before/after login, consent, UTM/click ids, deep-link params.
4. Flag **PII in event or user attributes** (phone, email, address, names) as a defect.
5. Optionally check aggregate volumes by platform over a window to spot "fires on Android
   only" or naming drift. State clearly that aggregates do not prove payloads.
6. Use `analytics-event-auditor` or a vendor-specific audit skill if installed.

## W7. Feature-flag / experiment validation

1. Read flag config: environments, targeting rules, rollout %, variants, default/fallback.
2. Determine which variant a given test user should get and why.
3. Verify control and each treatment, sticky assignment across sessions/devices, excluded
   users, kill-switch behaviour, and fallback when the flag service is unreachable.
4. Capture flag state with every result. Never toggle flags without approval.

## W8. CI failure analysis

1. Read the failed run: job, step, failing tests, logs, artefacts (Allure/TestNG/trace).
2. Compare with the last green run: diff, env changes, dependency bumps, data changes.
3. Check whether the same test fails elsewhere (history) and whether prod/staging telemetry
   shows a matching error.
4. Classify: product defect · test defect · flaky (timing/order/shared state) · env/infra ·
   test data. For flaky/test defects use `flaky-test-debugger` if installed.
5. Recommend a disposition (fix, quarantine with ticket, rerun justified, raise bug).

## W9. Non-functional gate

- **Accessibility**: run available automated checks (axe/BrowserStack a11y); always list
  the manual checks still needed (keyboard, focus order, screen reader, zoom, contrast).
- **Performance**: approved target + traffic profile only. Start with a tiny smoke run;
  ask before any real load. Correlate with p95/p99 latency, error rate, saturation.
- **Security**: SAST/SCA (Semgrep/Trivy) on approved repos; DAST (ZAP/Burp/Snyk) only on
  explicitly authorised targets and never prod. Findings need triage, not just a list.

## W10. Release readiness & sign-off

1. Collect: build/commit, env, platforms tested, executed cases with statuses, open
   defects by severity, blocked/not-run coverage, flags & rollout plan, CI status, current
   error/telemetry signals, rollback plan.
2. Apply exit criteria (team's if known; otherwise: no open blocker/critical, all P0 cases
   PASS, blocked coverage explained).
3. Output a sign-off report with a **recommendation**. Go/no-go is a human decision; never
   approve, merge, deploy or post the sign-off without approval.

## W11. MCP setup assistant

1. Identify the host (Claude.ai, Claude Code, Desktop, Cursor, VS Code…) and what it
   supports (remote connectors, local stdio, both).
2. List currently connected servers and their visible tools. Note duplicates/overlaps.
3. Compare against the task and `references/mcp-catalog.md`; propose the **minimal** set
   with: why, source, maturity, auth model, runtime, permissions requested, risks.
4. Give exact setup steps/config for that host, but do not run or change config until
   approved. Never ask for API keys in chat; use OAuth or env vars/secret managers.
   Include Windows PowerShell variants for local setup.
5. After approval, connect one server at a time and verify with a harmless read.
6. Report: connected-and-verified · connected-not-authenticated · failed · not attempted.

---

## Orchestration examples

**Story → test plan:** Jira story + Confluence PRD + Figma frames + existing cases + PR
diff → gaps/questions, traceable suite. No writes.

**UI defect:** Jira bug → browser repro (screenshots, console, network) → Sentry error by
request id → read-only DB check of the entity → recent commits → triage note + bug draft.

**Payment retry/idempotency:** Postman collection + sandbox gateway reads + webhook/event
records + read-only DB → pending/failure/retry/duplicate/refund lifecycle verdicts. Never
touch live payment objects.

**Analytics on a new feature:** spec sheet + test user's event timeline (e.g. MoEngage) +
HAR from a staging session → missing/extra events and attributes, PII leaks, platform
gaps; aggregate volumes as supporting context only.

**Mobile release sanity:** release ticket + CI build + device cloud run + crash data +
analytics events → Android/iOS matrix and risk summary.

**CI failure:** failed run + Allure report + diff + telemetry → product vs test vs env vs
flaky disposition.

**Flag rollout:** flag config + controlled checks per variant + fallback test → per-variant
results with flag state recorded. No flag changes.
