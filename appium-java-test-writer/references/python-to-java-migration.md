# Python Appium (pytest) → Java Appium (TestNG) migration

## Structure mapping

| Python | Java |
|---|---|
| `conftest.py` driver fixture (`yield driver`) | `DriverFactory` (ThreadLocal) + `BaseTest` `@BeforeMethod` / `@AfterMethod(alwaysRun = true)` |
| fixture `scope="function"` / `"class"` / `"session"` | `@BeforeMethod` / `@BeforeClass` / `@BeforeSuite` |
| `pytest_runtest_makereport` hook for screenshots | `ITestResult` in `@AfterMethod` + `Allure.addAttachment` |
| `@pytest.mark.parametrize("a,b", [...])` | `@DataProvider` returning `Object[][]`, case ID as first column |
| `@pytest.mark.smoke` / `-m smoke` | `@Test(groups = "smoke")` + `<groups>` in testng.xml |
| `pytest-xdist -n 2` | `parallel="tests"` in testng.xml with per-device parameters |
| `pytest.ini` / `.env` | `config.properties` + `-D` overrides |
| `@allure.step("...")` | `@Step("...")` (needs aspectjweaver agent) |
| `allure.dynamic.link` / `@allure.testcase` | `Allure.link(...)` / `@TmsLink` |
| page module with locator tuples | screen class with `@AndroidFindBy` / `@iOSXCUITFindBy` fields |
| `pytest.skip("reason")` | `throw new SkipException("reason")` |
| `pytest.raises(X)` | `Assert.assertThrows(X.class, () -> ...)` |

## API mapping

| Python (Appium-Python-Client 2+/3+) | Java (java-client 9) |
|---|---|
| `webdriver.Remote(url, options=UiAutomator2Options().load_capabilities(caps))` | `new AndroidDriver(URI.create(url).toURL(), new UiAutomator2Options()...)` |
| desired caps dict `{"appium:udid": ...}` | typed setters `.setUdid(...)`, `.setApp(...)`, `.setSystemPort(...)` |
| `driver.find_element(AppiumBy.ACCESSIBILITY_ID, "x")` | `driver.findElement(AppiumBy.accessibilityId("x"))` or `@AndroidFindBy(accessibility = "x")` |
| `AppiumBy.ID, "pkg:id/x"` | `AppiumBy.id("pkg:id/x")` / `@AndroidFindBy(id = "pkg:id/x")` |
| `AppiumBy.ANDROID_UIAUTOMATOR, '...'` | `AppiumBy.androidUIAutomator("...")` / `@AndroidFindBy(uiAutomator = "...")` |
| `AppiumBy.IOS_PREDICATE, '...'` | `AppiumBy.iOSNsPredicateString("...")` / `@iOSXCUITFindBy(iOSNsPredicate = "...")` |
| `AppiumBy.IOS_CLASS_CHAIN, '...'` | `AppiumBy.iOSClassChain("...")` / `@iOSXCUITFindBy(iOSClassChain = "...")` |
| `WebDriverWait(driver, 15).until(EC.visibility_of_element_located(loc))` | `new WebDriverWait(driver, Duration.ofSeconds(15)).until(ExpectedConditions.visibilityOf(el))` |
| `time.sleep(3)` | **remove**; replace with the condition actually being waited for |
| `driver.implicitly_wait(10)` | **remove**; set implicit wait to `Duration.ZERO`, use explicit waits |
| `TouchAction(driver).press(...).move_to(...).release().perform()` | W3C `PointerInput` sequence or `mobile: swipeGesture` / `mobile: swipe` |
| `TouchAction(driver).long_press(el)` | `mobile: longClickGesture` (Android) / `mobile: touchAndHold` (iOS) |
| `driver.execute_script("mobile: scroll", {...})` | `driver.executeScript("mobile: scroll", Map.of(...))` |
| `driver.get_screenshot_as_png()` | `driver.getScreenshotAs(OutputType.BYTES)` |
| `driver.page_source` | `driver.getPageSource()` |
| `driver.press_keycode(4)` | `((AndroidDriver) driver).pressKey(new KeyEvent(AndroidKey.BACK))` |
| `driver.terminate_app(pkg)` / `activate_app` | `((InteractsWithApps) driver).terminateApp(pkg)` / `activateApp(pkg)` |
| `el.text` / `el.get_attribute("x")` | `el.getText()` / `el.getAttribute("x")` |
| `assert a == b` | `Assert.assertEquals(actual, expected, "message")` (note TestNG order: actual, expected) |
| `assert el.is_displayed()` | `Assert.assertTrue(screen.isDisplayed(el), "message")` via a waiting helper |

## Anti-patterns to fix during migration (note each in the migration table)

- Sleeps and implicit waits → explicit condition waits.
- Global/module-level `driver` → ThreadLocal via DriverFactory.
- Locators duplicated in tests → moved into screen classes.
- `if platform == "android":` branches scattered in tests → dual annotations on one field, or a single platform check inside the screen.
- Weak assertions (`assert el`, no message) → specific assertions with messages.
- Bare `try/except: pass` around steps → remove; let failures fail.

## Worked migration

### Python input

```python
# conftest.py
@pytest.fixture
def driver():
    caps = {"platformName": "Android", "appium:automationName": "UiAutomator2",
            "appium:app": "apps/demo.apk", "appium:udid": "emulator-5554"}
    d = webdriver.Remote("http://127.0.0.1:4723", options=UiAutomator2Options().load_capabilities(caps))
    d.implicitly_wait(10)
    yield d
    d.quit()

# test_login.py
@pytest.mark.parametrize("user,msg", [
    ("locked_out_user", "Sorry, this user has been locked out."),
    ("wrong_user", "Username and password do not match any user in this service."),
])
def test_login_errors(driver, user, msg):
    driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-Username").send_keys(user)
    driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-Password").send_keys("secret_sauce")
    driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-LOGIN").click()
    time.sleep(2)
    err = driver.find_element(AppiumBy.XPATH, '//*[@content-desc="test-Error message"]/android.widget.TextView')
    assert msg in err.text
```

### Java output

```java
// LoginScreen.java (excerpt)
@AndroidFindBy(accessibility = "test-Username")
@iOSXCUITFindBy(accessibility = "test-Username")
private WebElement username;
// ...password, loginButton likewise...

@AndroidFindBy(xpath = "//*[@content-desc='test-Error message']/android.widget.TextView") // child text view has no a11y id
@iOSXCUITFindBy(accessibility = "test-Error message") // TODO-VERIFY locator
private WebElement errorText;

@Step("Attempt login as {user}")
public LoginScreen attemptLogin(String user, String pass) {
    type(username, user);
    type(password, pass);
    tap(loginButton);
    return this;
}

public String errorMessage() { return textOf(errorText); } // waits for visibility instead of sleep(2)
```

```java
// LoginTest.java (excerpt)
@DataProvider(name = "loginErrors")
public static Object[][] loginErrors() {
    return new Object[][] {
        {"TC-L02", "locked_out_user", "Sorry, this user has been locked out."},
        {"TC-L03", "wrong_user", "Username and password do not match any user in this service."},
    };
}

@Test(dataProvider = "loginErrors", description = "Login error messages")
@Feature("Authentication") @Severity(SeverityLevel.NORMAL)
public void shouldShowErrorForInvalidLogin(String caseId, String user, String expected) {
    Allure.link(caseId, "tms", caseId);
    String actual = new LoginScreen(driver()).waitUntilLoaded()
            .attemptLogin(user, "secret_sauce")
            .errorMessage();
    assertTrue(actual.contains(expected), "Expected error containing: " + expected + " but was: " + actual);
}
```

### Migration table

| Python | Java | Changes beyond translation |
|---|---|---|
| conftest.py `driver` fixture | DriverFactory + BaseTest | ThreadLocal; implicit wait 10s → 0 with explicit waits; caps dict → UiAutomator2Options; failure screenshot + page source added |
| test_login.py `test_login_errors` | LoginTest.shouldShowErrorForInvalidLogin | `time.sleep(2)` → visibility wait; locators moved to LoginScreen; iOS locators added (error text TODO-VERIFY); case IDs added for traceability |
