# Level ladder, expectations and placement check

## What interviewers expect at each level

| Level | Knows | Can do | Talks about |
|---|---|---|---|
| L0 Foundation | SDLC/STLC, testing types, bug life cycle, severity vs priority, basic SQL, programming basics | Write clear test cases and bug reports, test a simple feature end to end | Projects from college or manual work, willingness to learn |
| L1 Junior automation | One language (Java/Python/JS), one tool (Selenium/Playwright/Cypress), locators, waits, assertions, basic Git, API with Postman | Automate given test cases, fix simple failures, run tests in CI someone else set up | Scripts they wrote, bugs they found |
| L2 SDET | OOP, design patterns, framework layers, parallel runs, REST Assured or similar, SQL joins, CI pipelines, Docker basics | Build or extend a framework, debug flaky tests, design tests for a feature, API + UI coverage | Framework decisions, flaky-test fixes, measurable impact |
| L3 Senior SDET | Architecture trade-offs, test strategy, performance testing, contract testing, observability, mocking/service virtualisation | Own quality for a product area, choose tools, set up pipelines, mentor | Strategy, trade-offs, metrics, influencing developers and PMs |
| L4 Lead / Architect / Manager | Org-wide quality models, test infra at scale, cost/ROI, risk management, hiring and team growth | Define the quality strategy, run a QA team, design shared test platforms, report quality to leadership | Vision, decisions with business impact, people leadership, failures and lessons |

## Placement check (ask one at a time, no hints)

1. Fundamentals: "What is the difference between severity and priority? Give an example where they differ."
2. Fundamentals: "How would you test a login page? Name at least 8 test cases."
3. Automation: "What is the difference between an implicit and an explicit wait, and which do you prefer?"
4. Automation: "How would you run 200 UI tests in parallel without them interfering with each other?"
5. Design: "Your team releases weekly and regression takes three days. What would you change?"
6. Behavioural: "Tell me about a bug you found that others missed. What was the impact?"

Placement:
- Weak on 1-2 → L0.
- Solid on 1-2, weak on 3-4 → L1.
- Solid on 1-4, generic on 5 → L2.
- Solid on 1-5 with trade-offs and numbers → L3.
- Answers 5-6 with strategy, people and business impact → L4.
