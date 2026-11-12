---
name: flaky-test-debugger
description: Diagnose flaky or failing automated tests (Playwright, Selenium, Appium, REST Assured, TestNG/JUnit) from failure logs, stack traces, Playwright trace.zip files, screenshots, Allure/Surefire/TestNG XML results across runs, and the test code. Classifies the root cause with evidence, separates test bugs from real product bugs, and gives a concrete code fix plus a verification plan. Use this whenever the user shares a failing test, a stack trace, a trace or report, says a test "fails sometimes", "passes locally but fails in CI", "fails only in parallel", asks "why is this flaky", "debug this failure", or wants flakiness stats across runs, even if they don't use the word "flaky".
---

# Flaky Test Debugger

Goal: find **why** a test fails intermittently, prove it with evidence from the artifacts, and fix the cause rather than hide it. Retries and sleeps are not fixes; they're how flaky suites get worse.

## 1. Gather and extract evidence

Use whatever the user gave; ask for one missing artifact only if the diagnosis genuinely depends on it (usually the test code or the trace).

- **Playwright trace.zip**: run `python scripts/parse_pw_trace.py <trace.zip>` for an action timeline (durations, errors, retries inside actions), failed/slow network calls, and console errors. Then look at the screenshots near the failing action if present (`--extract-screens <dir>` writes them out).
- **Multiple result files** (Surefire/TestNG/JUnit XML from several runs, or a folder of them): run `python scripts/flake_stats.py <files-or-dirs...>` for per-test pass/fail counts, flip rate, and failure messages grouped by normalized signature. Different signatures for the same test usually mean different causes; don't merge them.
- **Logs/stack traces**: find the first real error (not the cascade after it), the exact failing line in test code, the wait/timeout values, and timestamps.
- **Screenshots**: what's actually on screen at failure: overlay, spinner, toast, error page, wrong variant, cookie banner, keyboard covering the element.
- **Test code**: the failing step plus its preceding 3–5 steps; setup/teardown; shared state (static fields, shared accounts, fixed test data, order dependencies).

## 2. Classify

Match the evidence to a category in `references/failure-signatures.md` (read it; it has exact error strings per framework). Main categories:

1. Synchronization / timing
2. Locator fragility / strictness
3. Overlay, animation, click interception
4. Test data and state coupling (order dependence, shared data, leftover state)
5. Parallel / concurrency (static or leaked driver/session, port clashes)
6. Environment / infrastructure (5xx, timeouts from backend, device/emulator, CI resources)
7. External dependencies (third-party services, A/B experiments, feature flags)
8. Time, date, locale, timezone
9. **Real product bug** (race condition or intermittent defect in the app itself)

Rules for classifying:
- Pick a primary cause and give a confidence (High/Medium/Low) with the specific evidence lines that support it. If two categories fit, say what would distinguish them (e.g. "if it also fails with thread-count=1 it's not concurrency").
- Category 9 is real: if the app shows an error state, a duplicate request, a wrong value after a correct action, or a backend 5xx, treat it as a possible product defect and say so. Don't "fix" the test to ignore it. Draft a short bug summary instead.
- When several tests fail, diagnose each one separately: different signatures usually mean different causes. Give one verdict per test, not one for the "flaky suite". A test that fails on every run is **not flaky**: report it as a consistent break (env data or product bug) and keep it out of flakiness fixes.
- Ignore noise explicitly: if the artifacts show errors that aren't on the failing path (analytics 503s, console warnings), say they're not the cause, so nobody chases them.
- Don't blame infrastructure without evidence (status codes, connection errors, resource exhaustion). "CI is slow" is a hypothesis, not a diagnosis.

## 3. Fix

Give the minimal code change as a before/after or diff on the user's actual code, in the user's framework and language. Prefer, in order:
1. Wait for the **right condition** (web-first assertion, response, element state, count) instead of time.
2. Make the locator unique and stable.
3. Remove the shared state: unique test data per test, cleanup in finally/after hooks, ThreadLocal sessions, no order dependence.
4. Control the environment: mock or stub the third-party call, pin the experiment variant / feature flag, freeze time or set timezone/locale explicitly.

Never propose as the fix: `Thread.sleep`/`waitForTimeout`, bigger global timeouts, blanket retries, `force: true` clicks, catching and ignoring the exception. If a retry or quarantine is warranted while the real fix lands, label it **temporary**, scope it to that test, and say what to track.

## 4. Verify

Give a concrete way to prove the fix, scaled to the observed failure rate (to see a 5% flake with ~95% confidence you need ~60 clean runs):
- TestNG: `@Test(invocationCount = 50, threadPoolSize = 4)` on the test temporarily, or a loop in CI.
- JUnit 5: `@RepeatedTest(50)`.
- Playwright (Node test runner): `npx playwright test <file> --repeat-each=50 --workers=4`.
- Also run with thread-count=1 vs N when concurrency is suspected, and isolated vs full suite when order dependence is suspected. Those comparisons are diagnostic, not just verification.

## Output format

1. **Verdict**: category, confidence, one-sentence root cause.
2. **Evidence**: the specific timeline lines / log lines / screenshot observations / stats that support it (quote short snippets).
3. **Fix**: code change(s).
4. **Verify**: commands/config and the pass criterion.
5. **Also check** (optional, max 3): other places in the code with the same pattern, or a product-bug summary if category 9.

Keep it tight. If evidence is insufficient, say what's missing and give the top 2 hypotheses with how to tell them apart, instead of guessing one.

## Confidentiality

Logs and traces often contain tokens, cookies, emails, phone numbers, and internal URLs. Don't repeat them in the answer beyond what's needed; mask them (e.g. `Bearer eyJ…[redacted]`) when quoting evidence.

## Bundled files

- `references/failure-signatures.md`: error strings → category → typical fix, for Playwright (Java/Node), Selenium, Appium, REST Assured, TestNG/JUnit.
- `scripts/parse_pw_trace.py`: Playwright trace.zip → action timeline, slow/failed actions, network failures, console errors; optional screenshot extraction.
- `scripts/flake_stats.py`: JUnit/Surefire/TestNG XML across runs → per-test pass rate, flips, grouped failure signatures.
