# Claude Skills for QA

Seventeen reusable [Claude skills](https://docs.claude.com) that automate the repetitive, judgement-heavy parts of QA and SDET work: turning a PRD into test cases, writing Playwright/Appium/REST Assured automation, auditing analytics tracking, debugging flaky tests, and testing AI features.

## What are Claude skills?

A skill is a folder with a `SKILL.md` file (a short description plus step-by-step instructions) and optional helper scripts, reference docs and templates. Claude reads the description of every installed skill and loads the full instructions only when your request matches, so you get a repeatable, expert workflow without pasting a long prompt each time.

## The skills

| Skill | What it does | When to use it |
|---|---|---|
| [`prd-to-test-cases`](prd-to-test-cases) | Reviews a PRD/design for contradictions and gaps first, then writes traceable, prioritized test cases and an Excel workbook | You have a PRD, user stories or Figma screens and need test cases or a spec review |
| [`playwright-java-test-writer`](playwright-java-test-writer) | Converts manual cases into Playwright Java tests with Page Objects, ThreadLocal sessions, TestNG and Allure | You have manual cases and want parallel-safe web automation |
| [`appium-java-test-writer`](appium-java-test-writer) | Writes cross-platform Appium Java tests, or migrates Python/pytest Appium tests to Java | You are automating an Android/iOS app or porting Python mobile tests |
| [`api-test-writer`](api-test-writer) | Generates REST Assured tests, JSON schema checks and a coverage matrix from cURL, Postman, OpenAPI or HAR | You have an API description and want contract and negative tests |
| [`analytics-event-auditor`](analytics-event-auditor) | Checks captured events (HAR, exports) against a tracking spec, including naming, types, duplicates and PII leaks | You need to verify analytics tracking for a feature |
| [`flaky-test-debugger`](flaky-test-debugger) | Classifies the root cause of flaky tests from logs, traces and result XML, and proposes a real fix | A test fails intermittently, in CI only, or in parallel only |
| [`ai-feature-testing`](ai-feature-testing) | Property-based test design for LLM, ranking, media and agent features | You must QA a feature whose output is not deterministic |
| [`universal-project-intelligence-sdet`](universal-project-intelligence-sdet) | Analyzes any repo or monorepo into evidence-based documentation, then assists with testability, test design, defect investigation and regression planning | You are onboarding to an unfamiliar project or need an SDET-level view of a codebase |
| [`bug-report-writer`](bug-report-writer) | Turns rough notes, screenshots, recordings or failing tests into ready-to-file bug reports with steps, expected vs actual and severity | You have raw findings and need a clean Jira/Linear/GitHub bug |
| [`cross-platform-parity-checker`](cross-platform-parity-checker) | Compares a screen or flow across iOS, Android, web, Figma and the PRD and lists every mismatch with severity | You need to confirm platforms and design agree |
| [`test-execution-reporter`](test-execution-reporter) | Turns raw results (sheets, Allure, TestNG/JUnit XML, Playwright, CI output) into a stakeholder report and a release go/no-go | You must summarise a test run or give QA sign-off |
| [`regression-scope-planner`](regression-scope-planner) | Picks what to regression-test from a PR diff, commit log or ticket list, based on risk instead of "run everything" | You need a risk-based regression scope for a release or hotfix |
| [`ab-experiment-qa`](ab-experiment-qa) | Builds the variant x platform x user-state test matrix and checks bucketing, isolation and per-variant analytics | You are testing an A/B experiment or feature-flag rollout |
| [`production-issue-rca`](production-issue-rca) | Structured root-cause analysis for production tickets: timeline, ranked hypotheses, evidence and resolution | A ticket says data or payments are wrong and you need the cause |
| [`sql-test-data-finder`](sql-test-data-finder) | Writes safe, read-only SQL to find test accounts and records matching a plain-English scenario, plus data-integrity checks | You need a test user or want to verify data after a migration |
| [`synthetic-test-data-generator`](synthetic-test-data-generator) | Generates realistic but fake users, orders and other entities as CSV, JSON, SQL seed or code fixtures | You need test data without touching real customer data |
| [`api-contract-diff`](api-contract-diff) | Compares two API contract versions (OpenAPI, JSON samples, HAR) and classifies changes as breaking, risky or safe | An API changed and you need to know what breaks clients |

## Example prompts

- **prd-to-test-cases**: "Here is the PRD for our coupon feature. Find contradictions and gaps, then write prioritized test cases as an Excel workbook."
- **playwright-java-test-writer**: "Automate these 12 manual login and cart test cases in Playwright Java against saucedemo.com."
- **appium-java-test-writer**: "Convert this pytest Appium login suite to Java with TestNG and Allure, and fix any weak assertions."
- **api-test-writer**: "Here is a Postman collection for the booking API. Write REST Assured tests with schema validation and a coverage matrix."
- **analytics-event-auditor**: "Audit this HAR capture against tracking_spec.csv and flag missing events, wrong types and PII."
- **flaky-test-debugger**: "This test passes locally but fails in CI about 1 run in 10. Here are the stack trace, trace.zip and Surefire results. Why?"
- **ai-feature-testing**: "We are shipping an AI support chatbot. Design test cases and assertions, and tell me how to test it when the answers differ every run."
- **bug-report-writer**: "Turn these rough notes and the attached screenshot into a Jira bug with steps, expected vs actual and a severity."
- **cross-platform-parity-checker**: "Compare the order summary screen on iOS, Android and web against the Figma frame and list every mismatch."
- **test-execution-reporter**: "Here is the Allure/TestNG report from last night's run. Write a sign-off summary and a go/no-go for the release."
- **regression-scope-planner**: "Here is the PR diff for the checkout hotfix. What should I regression-test, and what can I safely skip?"
- **ab-experiment-qa**: "Write a test plan for this A/B experiment on the home banner across Android, iOS and web, including bucketing and analytics."
- **production-issue-rca**: "A customer says they paid but the order still shows pending. Here are the ticket and logs. Find the root cause."
- **sql-test-data-finder**: "Write a read-only query to find a user with an overdue renewal and an active cart in staging."
- **synthetic-test-data-generator**: "Generate 50 fake users with Indian addresses and phone numbers as CSV, including some invalid edge cases."
- **api-contract-diff**: "Compare the old and new booking API OpenAPI specs and tell me which changes will break existing clients."
- **universal-project-intelligence-sdet**: "I just joined this repo. Map the architecture and business flows, assess testability, and propose a regression plan."

## Install a skill

**Claude.ai / Claude desktop:** zip the skill folder (so `SKILL.md` sits inside the folder) and upload it under *Settings → Capabilities → Skills*.

**Claude Code:** copy the folder into your skills directory, then restart the session.

```bash
git clone https://github.com/Mcube333/claude-skills-for-qa.git
cp -r claude-skills-for-qa/flaky-test-debugger ~/.claude/skills/        # personal, all projects
# or: cp -r claude-skills-for-qa/flaky-test-debugger <your-repo>/.claude/skills/   # one project
```

Then just describe your task. Claude picks the matching skill from its description. Some skills ship Python helpers (`audit_events.py`, `flake_stats.py`, `parse_pw_trace.py`, `build_workbook.py`); they need Python 3, and the Excel builder needs `openpyxl`.

## Why I built these

QA work has a lot of repeatable thinking: reading a spec for holes, checking whether tracking events match a plan, working out why a test flakes, converting manual cases into maintainable code. Doing it by hand is slow and inconsistent. AI is good at the mechanical 80% when it is given a method, and bad when it is improvised. These skills capture the method: analytics audits that check events mechanically before applying judgement, root-cause analysis that demands evidence instead of adding retries, and test design that traces every case back to a requirement. The goal is not to replace the tester but to spend human attention on the parts that need it.

## License

MIT, see [LICENSE](LICENSE).
