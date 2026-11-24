# Learning paths and study plans

Build a day-by-day plan from the interview date backwards: 60% practice (questions, coding, mocks), 40% learning.
Always end with a full mock interview 1-2 days before the interview.

## L0 → L1 (manual to automation), 6-8 weeks
1. Testing fundamentals: SDLC/STLC, test design techniques (equivalence, boundary, decision table, state transition), bug reporting.
2. Programming basics in one language (Java or Python): variables, conditions, loops, collections, functions, classes.
3. Web basics: HTML, CSS selectors, how a browser loads a page, DevTools.
4. One automation tool: Selenium or Playwright - locators, waits, assertions, Page Object Model.
5. Test runner: TestNG/JUnit or pytest; Git basics; running tests from the command line.
6. API testing with Postman: methods, status codes, JSON, auth.
7. SQL: SELECT, WHERE, JOIN, GROUP BY.
8. Build one small public project (login + search + cart on a demo site) with a README.

## L1 → L2 (junior to SDET), 4-6 weeks
1. OOP and design patterns used in frameworks (POM, Factory, Builder, Singleton risks).
2. Framework design: layers, config per environment, test data, reporting, retries.
3. Parallel execution and thread safety (ThreadLocal, isolated data).
4. API automation (REST Assured / requests / Playwright API) with schema validation.
5. CI/CD: GitHub Actions or Jenkins pipeline, artifacts, secrets; Docker basics.
6. Debugging flaky tests; reading traces and logs.
7. Test design for real features (cart, payments, search), risk-based regression.

## L2 → L3 (SDET to senior), 4-6 weeks
1. Test strategy for a whole product; test pyramid trade-offs; what not to automate.
2. Contract testing, mocking and service virtualisation; testing microservices and async flows.
3. Performance testing (k6/JMeter/Gatling): profiles, percentiles, SLOs.
4. Mobile automation at scale; device clouds.
5. Observability for QA: logs, metrics, tracing; testing in production safely (feature flags, canaries).
6. Quality metrics: escaped defects, flakiness rate, lead time, coverage that matters.
7. Mentoring and code review for test code.

## L3 → L4 (senior to lead/architect/manager), ongoing
1. Org-wide quality strategy and operating model (who owns quality, shift-left, QA in squads vs central).
2. Test infrastructure design: grids, device farms, test data platforms, environments, cost.
3. Measuring and reporting quality to leadership; ROI of automation.
4. Hiring, interviewing, career ladders, coaching under-performers.
5. Stakeholder management, saying no with data, release governance.
6. Risk management, compliance and privacy in testing.

## Two-week crash plan (any level)
- Days 1-3: fundamentals and placement-check gaps.
- Days 4-7: tool and framework depth at target level; one coding problem a day.
- Days 8-10: scenario and design rounds; prepare 6-8 STAR stories.
- Days 11-12: resume deep-dive questions; mock interview.
- Day 13: revise the mistake log. Day 14: light review and rest.
