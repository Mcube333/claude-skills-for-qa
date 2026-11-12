# Appium Java framework scaffold

Contents: 1. Layout · 2. pom.xml · 3. config · 4. DriverFactory · 5. BaseTest · 6. BaseScreen (waits + gestures) · 7. testng.xml (parallel devices) · 8. Gestures cheat sheet

Versions are known-good at time of writing; tell the user to bump to latest stable. Requires Appium 2 server with `uiautomator2` and/or `xcuitest` drivers installed.

## 1. Layout

```
src/main/java/com/example/
  config/ConfigReader.java
  driver/DriverFactory.java
  screens/BaseScreen.java
  screens/<Name>Screen.java
  components/<Name>.java
src/test/java/com/example/
  base/BaseTest.java
  tests/<feature>/<Feature>Test.java
  data/<Feature>Data.java
src/test/resources/
  config.properties
  testng-android.xml
  testng-ios.xml
apps/            (gitignored .apk/.app/.ipa)
```

## 2. pom.xml

```xml
<properties>
  <maven.compiler.source>17</maven.compiler.source>
  <maven.compiler.target>17</maven.compiler.target>
  <aspectj.version>1.9.22</aspectj.version>
</properties>
<dependencies>
  <dependency>
    <groupId>io.appium</groupId>
    <artifactId>java-client</artifactId>
    <version>9.3.0</version> <!-- brings a compatible Selenium -->
  </dependency>
  <dependency>
    <groupId>org.testng</groupId>
    <artifactId>testng</artifactId>
    <version>7.10.2</version>
    <scope>test</scope>
  </dependency>
  <dependency>
    <groupId>io.qameta.allure</groupId>
    <artifactId>allure-testng</artifactId>
    <version>2.29.0</version>
  </dependency>
</dependencies>
<!-- surefire + aspectjweaver javaagent exactly as in a Playwright/Selenium Allure setup;
     point suiteXmlFile at ${suite} so you can run -Dsuite=src/test/resources/testng-android.xml -->
```

## 3. config.properties

```
appiumUrl=http://127.0.0.1:4723
android.app=apps/app-debug.apk
android.appPackage=com.example.app
android.appActivity=.MainActivity
ios.app=apps/MyApp.app
ios.bundleId=com.example.app
ios.platformVersion=17.5
explicitWaitSec=15
android.autoGrantPermissions=true   # set false (-D) for tests that verify permission dialogs
noReset=false
newCommandTimeoutSec=120
```

ConfigReader: same pattern as any Java framework — load properties from classpath, let `-Dkey=value` override.

## 4. DriverFactory (ThreadLocal)

```java
package com.example.driver;

import com.example.config.ConfigReader;
import io.appium.java_client.AppiumDriver;
import io.appium.java_client.android.AndroidDriver;
import io.appium.java_client.android.options.UiAutomator2Options;
import io.appium.java_client.ios.IOSDriver;
import io.appium.java_client.ios.options.XCUITestOptions;

import java.net.URI;
import java.net.URL;
import java.nio.file.Paths;
import java.time.Duration;

public final class DriverFactory {
    private static final ThreadLocal<AppiumDriver> DRIVER = new ThreadLocal<>();
    private static final ThreadLocal<String> PLATFORM = new ThreadLocal<>();

    private DriverFactory() {}

    /** platform/udid/port come from testng.xml parameters so each thread drives its own device. */
    public static AppiumDriver start(String platform, String udid, int port) {
        try {
            URL server = URI.create(ConfigReader.get("appiumUrl")).toURL();
            Duration cmdTimeout = Duration.ofSeconds(ConfigReader.getInt("newCommandTimeoutSec"));
            AppiumDriver driver;
            if ("ios".equalsIgnoreCase(platform)) {
                XCUITestOptions opts = new XCUITestOptions()
                        .setUdid(udid)
                        .setApp(Paths.get(ConfigReader.get("ios.app")).toAbsolutePath().toString())
                        .setBundleId(ConfigReader.get("ios.bundleId"))
                        .setPlatformVersion(ConfigReader.get("ios.platformVersion"))
                        .setWdaLocalPort(port)
                        .setNewCommandTimeout(cmdTimeout);
                driver = new IOSDriver(server, opts);
            } else {
                UiAutomator2Options opts = new UiAutomator2Options()
                        .setUdid(udid)
                        .setApp(Paths.get(ConfigReader.get("android.app")).toAbsolutePath().toString())
                        .setAppPackage(ConfigReader.get("android.appPackage"))
                        .setAppActivity(ConfigReader.get("android.appActivity"))
                        .setSystemPort(port)
                        .setAutoGrantPermissions(ConfigReader.getBool("android.autoGrantPermissions"))
                        .setNoReset(ConfigReader.getBool("noReset"))
                        .setNewCommandTimeout(cmdTimeout);
                driver = new AndroidDriver(server, opts);
            }
            driver.manage().timeouts().implicitlyWait(Duration.ZERO); // explicit waits only
            DRIVER.set(driver);
            PLATFORM.set(platform.toLowerCase());
            return driver;
        } catch (Exception e) {
            throw new IllegalStateException("Could not start " + platform + " session on " + udid, e);
        }
    }

    public static AppiumDriver driver() { return DRIVER.get(); }
    public static boolean isIOS() { return "ios".equals(PLATFORM.get()); }

    public static void stop() {
        try { if (DRIVER.get() != null) DRIVER.get().quit(); }
        finally { DRIVER.remove(); PLATFORM.remove(); }
    }
}
```

## 5. BaseTest

```java
package com.example.base;

import com.example.driver.DriverFactory;
import io.appium.java_client.AppiumDriver;
import io.qameta.allure.Allure;
import org.openqa.selenium.OutputType;
import org.testng.ITestResult;
import org.testng.annotations.*;

import java.io.ByteArrayInputStream;

public abstract class BaseTest {

    protected AppiumDriver driver() { return DriverFactory.driver(); }

    @Parameters({"platform", "udid", "port"})
    @BeforeMethod(alwaysRun = true)
    public void setUp(@Optional("android") String platform,
                      @Optional("emulator-5554") String udid,
                      @Optional("8200") String port) {
        DriverFactory.start(platform, udid, Integer.parseInt(port));
    }

    @AfterMethod(alwaysRun = true)
    public void tearDown(ITestResult result) {
        try {
            if (!result.isSuccess() && driver() != null) {
                Allure.addAttachment("Screenshot on failure", "image/png",
                        new ByteArrayInputStream(driver().getScreenshotAs(OutputType.BYTES)), "png");
                Allure.addAttachment("Page source on failure", "text/xml", driver().getPageSource(), "xml");
            }
        } catch (Exception e) {
            System.err.println("Failure-artifact capture failed: " + e.getMessage());
        } finally {
            DriverFactory.stop();
        }
    }
}
```

## 6. BaseScreen (waits + gestures)

```java
package com.example.screens;

import com.example.config.ConfigReader;
import com.example.driver.DriverFactory;
import io.appium.java_client.AppiumBy;
import io.appium.java_client.AppiumDriver;
import io.appium.java_client.pagefactory.AppiumFieldDecorator;
import org.openqa.selenium.Dimension;
import org.openqa.selenium.StaleElementReferenceException;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.interactions.PointerInput;
import org.openqa.selenium.interactions.Sequence;
import org.openqa.selenium.support.PageFactory;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;
import java.util.List;
import java.util.Map;

public abstract class BaseScreen {
    protected final AppiumDriver driver;
    protected final WebDriverWait wait;

    protected BaseScreen(AppiumDriver driver) {
        this.driver = driver;
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(ConfigReader.getInt("explicitWaitSec")));
        this.wait.ignoring(StaleElementReferenceException.class); // lists/carousels re-render on mobile
        // Zero lookup timeout in the decorator: waiting is done explicitly below.
        PageFactory.initElements(new AppiumFieldDecorator(driver, Duration.ZERO), this);
    }

    /** Each screen overrides with a reliable "screen is ready" element. */
    public abstract BaseScreen waitUntilLoaded();

    protected WebElement visible(WebElement el) { return wait.until(ExpectedConditions.visibilityOf(el)); }
    protected void tap(WebElement el) { wait.until(ExpectedConditions.elementToBeClickable(el)).click(); }
    protected void type(WebElement el, String text) { visible(el).clear(); el.sendKeys(text); }
    protected void waitGone(WebElement el) { wait.until(ExpectedConditions.invisibilityOf(el)); }
    protected String textOf(WebElement el) { return visible(el).getText(); }

    public boolean isDisplayed(WebElement el) {
        try { return visible(el).isDisplayed(); } catch (Exception e) { return false; }
    }

    /** Scroll until an element with visible text is on screen. */
    protected void scrollToText(String text) {
        if (DriverFactory.isIOS()) {
            driver.executeScript("mobile: scroll", Map.of(
                    "direction", "down", "predicateString", "label == '" + text + "'"));
        } else {
            driver.findElement(AppiumBy.androidUIAutomator(
                    "new UiScrollable(new UiSelector().scrollable(true))"
                            + ".scrollIntoView(new UiSelector().text(\"" + text + "\"))"));
        }
    }

    /** Cross-platform vertical swipe using W3C actions (TouchAction is removed in java-client 9). */
    protected void swipeUp() {
        Dimension size = driver.manage().window().getSize();
        int x = size.width / 2, startY = (int) (size.height * 0.75), endY = (int) (size.height * 0.25);
        PointerInput finger = new PointerInput(PointerInput.Kind.TOUCH, "finger");
        Sequence swipe = new Sequence(finger, 1)
                .addAction(finger.createPointerMove(Duration.ZERO, PointerInput.Origin.viewport(), x, startY))
                .addAction(finger.createPointerDown(PointerInput.MouseButton.LEFT.asArg()))
                .addAction(finger.createPointerMove(Duration.ofMillis(600), PointerInput.Origin.viewport(), x, endY))
                .addAction(finger.createPointerUp(PointerInput.MouseButton.LEFT.asArg()));
        driver.perform(List.of(swipe));
    }
}
```

`ExpectedConditions.visibilityOf` on a PageFactory proxy is fine: WebDriverWait ignores `NotFoundException` while polling.

## 7. testng-android.xml (parallel devices)

```xml
<!DOCTYPE suite SYSTEM "https://testng.org/testng-1.0.dtd">
<suite name="Android" parallel="tests" thread-count="2">
  <test name="Pixel-7">
    <parameter name="platform" value="android"/>
    <parameter name="udid" value="emulator-5554"/>
    <parameter name="port" value="8200"/>
    <packages><package name="com.example.tests.*"/></packages>
  </test>
  <test name="Pixel-4">
    <parameter name="platform" value="android"/>
    <parameter name="udid" value="emulator-5556"/>
    <parameter name="port" value="8201"/>
    <packages><package name="com.example.tests.*"/></packages>
  </test>
</suite>
```

`port` is `systemPort` for Android and `wdaLocalPort` for iOS; it must be unique per parallel device.

## 8. Gestures cheat sheet

| Need | Android | iOS |
|---|---|---|
| Scroll to text | `AppiumBy.androidUIAutomator("new UiScrollable(...).scrollIntoView(new UiSelector().text(\"X\"))")` | `executeScript("mobile: scroll", Map.of("direction","down","predicateString","label == 'X'"))` |
| Swipe in element | `executeScript("mobile: swipeGesture", Map.of("elementId", ((RemoteWebElement) el).getId(), "direction","left","percent",0.75))` | `executeScript("mobile: swipe", Map.of("elementId", ((RemoteWebElement) el).getId(), "direction","left"))` |
| Long press | `executeScript("mobile: longClickGesture", Map.of("elementId", id, "duration", 1500))` | `executeScript("mobile: touchAndHold", Map.of("elementId", id, "duration", 1.5))` |
| Back | `((AndroidDriver) driver).pressKey(new KeyEvent(AndroidKey.BACK))` | tap the nav bar back button |
| Hide keyboard | `((AndroidDriver) driver).hideKeyboard()` | tap a "Done"/return key or outside the field |
| Deep link | `driver.get("myapp://path")` or `executeScript("mobile: deepLink", Map.of("url", "...", "package", pkg))` | `executeScript("mobile: deepLink", Map.of("url","...","bundleId", id))` |
| Cross-platform swipe | W3C `PointerInput` sequence (BaseScreen.swipeUp) | same |

Note iOS `touchAndHold` duration is in seconds; Android `longClickGesture` in milliseconds.
