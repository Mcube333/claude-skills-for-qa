# Claude Skills for QA

Seven reusable [Claude skills](https://docs.claude.com) that automate the repetitive, judgement-heavy parts of QA and SDET work: turning a PRD into test cases, writing Playwright/Appium/REST Assured automation, auditing analytics tracking, debugging flaky tests, and testing AI features.

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

## Example prompts

- **prd-to-test-cases**: "Here is the PRD for our coupon feature. Find contradictions and gaps, then write prioritized test cases as an Excel workbook."
- **playwright-java-test-writer**: "Automate these 12 manual login and cart test cases in Playwright Java against saucedemo.com."
- **appium-java-test-writer**: "Convert this pytest Appium login suite to Java with TestNG and Allure, and fix any weak assertions."
- **api-test-writer**: "Here is a Postman collection for the booking API. Write REST Assured tests with schema validation and a coverage matrix."
- **analytics-event-auditor**: "Audit this HAR capture against tracking_spec.csv and flag missing events, wrong types and PII."
- **flaky-test-debugger**: "This test passes locally but fails in CI about 1 run in 10. Here are the stack trace, trace.zip and Surefire results. Why?"
- **ai-feature-testing**: "We are shipping an AI support chatbot. Design test cases and assertions, and tell me how to test it when the answers differ every run."

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
