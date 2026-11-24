# Question bank (topics and representative questions)

Use as a menu, not a script. Add follow-ups. Levels: [0] foundation, [1] junior automation, [2] SDET,
[3] senior SDET, [4] lead / architect / manager.

## Testing fundamentals (start here for L0)
- [0] What is software testing and why is it needed?
- [0] SDLC vs STLC; where does testing start?
- [0] Verification vs validation.
- [0] Functional vs non-functional testing; give examples of each.
- [0] Smoke vs sanity vs regression testing.
- [0] Black-box vs white-box vs grey-box testing.
- [0] Bug life cycle; who moves a bug between states?
- [0] Severity vs priority with an example where they differ.
- [0] What makes a good test case? Write 5 for a login page.
- [0] Equivalence partitioning and boundary value analysis with an example (age field 18-60).
- [0] What do you do when a developer says "it works on my machine"?
- [1] Test plan vs test strategy.
- [1] Entry and exit criteria for a test cycle.
- [1] What would you automate first in a new project, and what would you keep manual?

## Programming basics (L0-L1)
- [0] Difference between a class and an object.
- [0] What is a loop? Write one that prints even numbers from 1 to 20.
- [0] Array vs list; when do you use a map/dictionary?
- [1] What is an exception? How do you handle one?
- [1] Read a value from a properties/config file.

## Java and OOP
- [1] Difference between `==` and `equals()`; why override `hashCode()` with `equals()`?
- [1] `String` vs `StringBuilder` vs `StringBuffer`.
- [1] Checked vs unchecked exceptions; where do you use custom exceptions in a framework?
- [2] `HashMap` internals; what happens on collision; why is `ConcurrentHashMap` used in parallel tests?
- [2] Explain `ThreadLocal` and why automation frameworks use it.
- [2] Interface vs abstract class (Java 8+ default methods) with a framework example.
- [2] Streams: filter/map/collect example; when not to use streams.
- [3] Design patterns in test frameworks: Page Object, Factory, Singleton (and its risks in parallel runs), Builder for test data, Strategy for environments.
- [3] Immutability and records for test data; why it reduces flakiness.

## Web automation (Selenium / Playwright)
- [1] Locator strategy priority and why (ids, data-testid, accessibility roles, CSS vs XPath).
- [1] Implicit vs explicit vs fluent waits; why mixing them is a problem.
- [2] Playwright auto-waiting and web-first assertions vs Selenium waits.
- [2] Handling iframes, multiple tabs, file upload/download, alerts, shadow DOM.
- [2] How do you run tests in parallel safely? (thread-local sessions, isolated data, no shared state)
- [2] Playwright browser vs context vs page; what is isolated where.
- [3] Selenium Grid vs Playwright remote server vs cloud providers: trade-offs.
- [3] Network interception: mocking APIs, blocking third parties, asserting requests (analytics).

## Mobile (Appium)
- [1] Appium architecture (client, server, driver, UiAutomator2/XCUITest).
- [2] Native vs hybrid vs web app automation; switching contexts.
- [2] Gestures with W3C actions; scrolling to elements.
- [2] Real devices vs emulators vs cloud (LambdaTest/BrowserStack): when each.
- [3] Making mobile suites parallel and stable; app state reset strategies.

## API testing
- [1] Status codes you check and what each means for a test.
- [1] PUT vs PATCH vs POST; idempotency.
- [2] REST Assured: request/response spec, schema validation, extracting values, chaining calls.
- [2] Positive, negative, boundary and contract tests for one endpoint.
- [2] Auth: tokens, refresh, testing expired/invalid tokens.
- [3] Contract testing and backward compatibility for mobile clients.
- [3] Testing async systems: webhooks, queues, eventual consistency.

## Test frameworks and design
- [1] TestNG annotations order; groups; DataProvider; parallel attribute.
- [2] Retry analyzers: when helpful, when they hide bugs.
- [2] Reporting (Allure/Extent): what to attach on failure.
- [2] Config for multiple environments; secrets handling.
- [3] Design a framework from scratch for web + API + mobile: layers, modules, CI, reporting, data.
- [3] How do you measure automation value (coverage, defect leakage, time saved, flakiness rate)?

## Test design and strategy
- [1] Equivalence partitioning, boundary values, decision tables, state transitions.
- [2] "How would you test a cart/checkout/payment page?"
- [2] Risk-based regression selection for a release.
- [2] Testing A/B experiments and feature flags.
- [3] Shift-left: what QA does before code is written (PRD/design review).
- [3] Test pyramid vs reality; what you would not automate.

## Flaky tests and debugging
- [2] A test passes locally, fails in CI. Walk through your investigation.
- [2] Common causes of flakiness and fixes for each.
- [3] Quarantine policy and flakiness metrics.

## SQL and data
- [1] Joins (inner, left), GROUP BY with HAVING.
- [2] Find duplicates; second highest salary; records in A not in B.
- [2] Validate that order totals equal the sum of line items.
- [3] Testing a data migration.

## CI/CD and DevOps
- [1] What runs on every PR vs nightly vs before release?
- [2] GitHub Actions/Jenkins pipeline for tests: matrix, caching, artifacts, secrets.
- [2] Docker for test runs: why, and what goes in the image.
- [3] Test environments and test data management at scale.

## Performance
- [2] Load vs stress vs spike vs soak testing.
- [2] p95/p99 latency; why averages mislead.
- [3] Setting SLO thresholds and making performance a CI gate.

## Analytics and privacy
- [2] How do you test analytics events? (spec, payloads, duplicates, naming)
- [2] What is PII and where can it leak in a product?

## Testing AI features
- [2] How do you test a feature whose output is not deterministic (LLM, recommendations)?
- [3] Metrics and guardrails for AI features: accuracy, hallucination, safety, regression across model versions.

## Leadership and strategy (L3-L4)
- [3] How do you decide the test strategy for a new product area?
- [3] How do you get developers to own quality without losing QA's role?
- [3] How do you mentor a junior who writes flaky tests?
- [4] How do you structure a QA team across many squads?
- [4] What quality metrics do you report to leadership, and which ones do you avoid?
- [4] How do you calculate and present the ROI of test automation?
- [4] How do you hire SDETs? What do you look for in an interview?
- [4] A release you blocked turned out fine; the business is unhappy. What do you do?
- [4] How do you handle an under-performing team member?
- [4] Budget is cut by 30%. What do you keep, what do you drop?

## Behavioural
- Tell me about yourself (90 seconds).
- A bug you found that others missed.
- A time you pushed back on a release.
- Conflict with a developer or PM.
- A failure and what you changed afterwards.
- How you used AI tools to improve your work.
- Why are you leaving / why this company?
