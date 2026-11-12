---
name: appium-java-test-writer
description: Write Appium Java mobile automation tests (Android and iOS) from manual test cases, or migrate existing Python/Appium (pytest) tests to Java - using ThreadLocal drivers for parallel devices, explicit condition-based waits, cross-platform Page Object Model, W3C gestures, TestNG and Allure. Use this whenever the user pastes mobile/app test cases and wants them automated, shares Python Appium code and wants it in Java, asks to "convert pytest to Java", "port to java-client", "automate this Android/iOS flow", "write Appium tests", or wants to scaffold an Appium Java framework, even if they don't say "Appium" but are clearly automating a native or hybrid mobile app in Java.
---

# Appium Java Test Writer

Produce mobile tests that look owned by an SDET: one codebase for Android and iOS, parallel-safe across devices, no sleeps, gestures that work on java-client 9+, and Allure reports that trace back to manual case IDs. Also handles Python → Java migration, which is a common real-world task and worth doing faithfully rather than just transliterating.

## Decide the mode

- **Manual cases → Java**: follow Workflow A.
- **Python/Appium code → Java**: follow Workflow B. Read `references/python-to-java-migration.md` first.
- **Scaffold a framework**: generate the files in `references/framework-scaffold.md`, adapted to the user's app and platforms.

If the user shares any existing Java framework files (BaseTest, a screen class, testng.xml, capabilities), mirror their conventions over the reference ones.

## Workflow A: manual cases → tests

1. **Normalize** each case into: ID, title, priority, platform(s), preconditions, test data, steps, expected results. Note platform-specific steps (Android back button, iOS permission alert).
2. **Screens and components**: one class per screen; reusable widgets (bottom nav, toolbar, bottom sheet) as component classes composed into screens. Screen methods express user intent and carry Allure `@Step("...")`. Navigating actions return the next screen object.
3. **Locators** — cross-platform via annotations on the same field:
   ```java
   @AndroidFindBy(accessibility = "login-button")
   @iOSXCUITFindBy(accessibility = "login-button")
   private WebElement loginButton;
   ```
   Priority: accessibility id → Android resource-id / iOS name → UiAutomator / iOS predicate or class chain → XPath last (slow on iOS, brittle everywhere; comment why if used). If no page source, Appium Inspector output, or screenshots were provided, mark guesses `// TODO-VERIFY locator`. If only one platform's locator is known, write that one and leave the other annotation with a `TODO-VERIFY` rather than copying it blindly.
4. **Tests**: one `@Test` per case, behaviour-named method, `@TmsLink` with the case ID, `@Epic/@Feature/@Story/@Severity` (P0 → BLOCKER/CRITICAL, P1 → NORMAL, P2+ → MINOR). Data variants → `@DataProvider` with the case ID as first column and `Allure.link(caseId, "tms", caseId)` in the body. Every expected result becomes an assertion.
5. **Device/app state**: call out cases that need non-default capabilities (permission dialogs need `autoGrantPermissions=false`, onboarding needs a clean install / `noReset=false`, emulator-only features like fingerprint) and put them in a separate group or note the override.
6. **Preconditions**: prefer deep links (`driver.get("myapp://cart")` on Android, `mobile: deepLink`) or API setup over long tap sequences. Login preconditions via API/session where possible.
7. **Not automatable as written** (real SMS OTP, real payments, biometric without simulator support, subjective visual checks): list under "Not automated" with an alternative (test OTP, sandbox payment, `mobile: enrollBiometric`/`sendBiometricMatch` on simulators/emulators, visual comparison tool).

## Workflow B: Python → Java migration

1. Read `references/python-to-java-migration.md`.
2. Map structure first (conftest fixtures → BaseTest/factory, page modules → screen classes, `parametrize` → `@DataProvider`), then translate code.
3. Fix anti-patterns instead of porting them: `time.sleep` → explicit waits, `TouchAction`/`MultiAction` → W3C Actions or `mobile:` gestures, desired-capabilities dicts → `UiAutomator2Options`/`XCUITestOptions`, global driver → ThreadLocal.
4. Keep test intent and assertions identical. If the Python test asserted something weak (e.g. `assert element`) or hid failures (`try/except: pass`, assertions inside conditionals), fix it and call it out in the migration table, because the original test may never have been able to fail.
5. Output a **migration table**: `Python file/function | Java class/method | Changes beyond translation`.

## Waits: explicit and condition-based

- Implicit wait is **0**. Mixing implicit and explicit waits causes unpredictable timeouts.
- Never `Thread.sleep`. Use `WebDriverWait` with `ExpectedConditions` (`visibilityOf`, `elementToBeClickable`, `invisibilityOf`, `textToBePresentInElement`, `attributeToBe`) through helpers in `BaseScreen`.
- Wait for loaders/spinners to disappear rather than for time to pass.
- Timeouts come from config, not inline numbers.
- After an action that re-renders a list or carousel, wait for a signal that is always true afterwards (sheet closed, loader gone, list present, count equals expected). Don't wait for "first item text changed": the expected value may already be in place and the wait times out. BaseScreen's wait ignores `StaleElementReferenceException`, so re-query inside the condition.

## Gestures

java-client 9 removed `TouchAction`/`MultiAction`. Use:
- Scroll to element: Android `AppiumBy.androidUIAutomator("new UiScrollable(...).scrollIntoView(...)")`; iOS `mobile: scroll` with `predicateString`.
- Swipe/drag/long press: platform `mobile:` gestures (Android `mobile: swipeGesture`, `longClickGesture`; iOS `mobile: swipe`, `touchAndHold`) or a W3C `PointerInput` sequence in `BaseScreen` for cross-platform use.
See `references/framework-scaffold.md` → Gestures.

## Parallel safety

Driver lives in a `ThreadLocal<AppiumDriver>` created per test (or per class if the user asks for speed), always `remove()`d after `quit()`. Each parallel device needs its own `udid` and a unique `systemPort` (Android) / `wdaLocalPort` (iOS) from testng.xml parameters. No static drivers or static element state.

## Output format

1. **Files**: full compilable files with imports, each under its path heading. If more than ~3 files or the user wants to download, also write them to disk as a project folder.
2. **Traceability table** (Workflow A) or **migration table** (Workflow B).
3. **Not automated / gaps**.
4. **Needs verification**: count and list of `TODO-VERIFY` locators, assumed capabilities (app path, package/activity, bundle id), platform-only steps.

Keep prose short; the code is the deliverable.

## Confidentiality

For portfolio/public work, use package `com.example` (or the user's), a public demo app, and swap any company names, internal app ids, internal URLs, real phone numbers/emails, or proprietary event names for neutral ones. Mention the swap in one line.

## Reference files

- `references/framework-scaffold.md`: pom.xml, config, DriverFactory with ThreadLocal + Options classes, BaseTest with Allure screenshot/page-source on failure, BaseScreen with wait helpers and gestures, testng.xml for parallel devices.
- `references/python-to-java-migration.md`: side-by-side mapping of Python Appium/pytest idioms to Java/TestNG, plus a worked migration.
- `references/example-swaglabs.md`: manual cases → screens → tests on the public Sauce Labs sample app.
