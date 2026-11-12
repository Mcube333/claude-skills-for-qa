---
name: playwright-java-test-writer
description: Convert manual test cases into Playwright Java automation tests using a production-style framework - ThreadLocal browser sessions for parallel runs, condition-based waits (no sleeps), Page Object Model, TestNG and Allure reporting. Use this whenever the user pastes or uploads manual test cases (table, Excel rows, Jira/TestRail export, Gherkin, or plain numbered steps) and wants them automated in Java, asks to "automate these test cases", "write Playwright tests for this", "convert to POM", "add page objects", or wants to scaffold a Playwright Java framework, even if they don't say "Playwright" but are clearly working in a Java web-automation project.
---

# Playwright Java Test Writer

Turn manual test cases into maintainable Playwright Java tests that look like they were written by someone who owns the framework: parallel-safe, no flaky sleeps, page objects that hide locators, and Allure reports that trace back to the original test case IDs.

## Workflow

### 1. Parse the manual test cases

Extract for each case: **ID, title, priority/severity, preconditions, test data, steps, expected result per step**. Inputs vary (Excel rows, Jira exports, Gherkin, free text), so normalize them into this shape before writing code.

If a case is not automatable as written (needs OTP from a real phone, visual judgement like "looks correct", third-party payment with real money), do not fake it. List it under **Not automated** in the output with the reason and a suggestion (mock the API, use a test OTP, visual snapshot comparison).

### 2. Detect existing framework conventions first

If the user shares repo files (BaseTest, a page class, testng.xml, pom.xml), mirror them exactly: package names, base class names, naming style, assertion style, how config is read. Consistency with their codebase beats the reference style below.

If nothing is shared, use the scaffold in `references/framework-scaffold.md`. Only generate the scaffold files (BaseTest, PlaywrightFactory, BasePage, config) when the user asks for a framework or clearly has none; otherwise assume they exist and generate only page objects and tests.

### 3. Design page objects

- One class per page or reusable component (header, cart drawer, filter panel). Components get their own class and are composed into pages.
- Locators are `private final Locator` fields initialized in the constructor. Tests never call `page.locator(...)` directly.
- Page methods describe **user intent** (`login(user, pass)`, `addToCart(productName)`), not mechanics (`clickButton2`). Annotate them with Allure `@Step("...")` using parameter placeholders, so the report reads like the manual case.
- Actions that navigate return the next page object (fluent flow). Methods that stay on the page return `this` or void.
- Reuse existing page methods before adding new ones. If two steps map to the same intent, use one method.
- Expose state for assertions through intent-named getters returning `Locator` (e.g. `errorMessage()`), so tests can use web-first assertions.

**Locator priority** (most to least stable):
1. `getByTestId` (configure the attribute name once if the app uses `data-test`, `data-qa`, etc.)
2. `getByRole` with accessible name
3. `getByLabel` / `getByPlaceholder` / `getByText` for user-visible text
4. CSS on stable attributes
5. XPath, only as a last resort, with a comment saying why

If the user gave no DOM, HTML, or screenshots, you are guessing locators. Write the best guess and mark it `// TODO-VERIFY locator` so nothing silently ships with invented selectors. Mention the count of unverified locators in the summary.

### 4. Write the tests

- One `@Test` method per manual case. Method name = behaviour (`shouldShowErrorForLockedUser`), not the ID.
- Traceability: put the case ID in `@TmsLink("TC-012")` and in `description`. Add `@Epic`, `@Feature`, `@Story`, `@Severity` mapped from the case's priority (P0/Critical → `BLOCKER`/`CRITICAL`, P1 → `NORMAL`, P2+ → `MINOR`).
- Every expected result becomes an assertion. A step with no assertion means the manual check was dropped, so cross-check before finishing.
- Preconditions go into setup helpers or API calls, not long UI click-chains, when an API or deep link exists. For login preconditions (especially OTP/SSO), prefer an API login once and reuse it via `context.storageState()` / `Browser.NewContextOptions().setStorageStatePath(...)`.
- Repeated cases with different data → one test with a TestNG `@DataProvider`. `@TmsLink` is static, so pass the case ID as the first data column and call `Allure.link(caseId, "tms", caseId)` inside the test to keep per-row traceability. Keep test data out of the test body (data provider, JSON, or constants class). No real customer data, ever.
- Tests must be independent: no reliance on execution order, fresh context per test, clean up anything created.

### 5. Waits: condition-based only

This is the main source of flakiness, so treat it as a hard rule:

- Never use `Thread.sleep` or `page.waitForTimeout`.
- Prefer web-first assertions: `assertThat(locator).isVisible()`, `hasText`, `hasCount`, `assertThat(page).hasURL(...)`. They auto-retry.
- Actions already auto-wait for actionability; don't add redundant waits before `click()`/`fill()`.
- When an action triggers a network call whose result matters, wrap it: `page.waitForResponse(r -> r.url().contains("/cart") && r.ok(), () -> addButton.click())`.
- For spinners/loaders: `assertThat(loader).isHidden()`.
- For navigation: `page.waitForURL("**/checkout**")`.
- Custom timeouts come from config, never magic numbers inline.

See `references/framework-scaffold.md` → "Wait patterns" for snippets.

### 6. Parallel safety

All Playwright objects (Playwright, Browser, BrowserContext, Page) live in `ThreadLocal`s managed by the base class/factory and are created and closed per test method. Never store them in static fields or share a `Page` between tests. Page objects receive the `Page` via constructor. Static state in page objects is not allowed.

## Output format

Reply with, in this order:

1. **Files**: each file in its own code block with its full path as a heading (e.g. `src/test/java/com/example/pages/LoginPage.java`). Full, compilable files with imports, not fragments, unless the user asked for a snippet. If more than ~3 files or the user wants to download them, also write them to disk as a project folder.
2. **Traceability table**: `Case ID | Test method | Steps automated | Notes`.
3. **Not automated / gaps**: cases or steps skipped and why.
4. **Needs verification**: count and list of `TODO-VERIFY` locators, assumptions about test data or environment.

Keep prose short; the code is the deliverable.

## Confidentiality

When the user is building a public portfolio or the request mentions a public demo app, keep everything generic: package `com.example` (or what they specify), no company names, internal URLs, internal endpoints, real user data, or proprietary event names. If pasted manual cases contain those, swap them for neutral equivalents and say so in one line.

## Reference files

- `references/framework-scaffold.md`: pom.xml deps, PlaywrightFactory with ThreadLocals, BaseTest with tracing and Allure attachments on failure, BasePage, ConfigReader, testng.xml for parallel runs, wait pattern snippets. Read it when scaffolding or when you need the exact API shape.
- `references/example-saucedemo.md`: a complete worked example (manual cases → page objects → tests → traceability table) on the public saucedemo.com app. Read it to calibrate output style.
