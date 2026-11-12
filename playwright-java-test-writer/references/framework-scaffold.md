# Framework scaffold (Playwright Java + TestNG + Allure)

Contents: 1. Project layout · 2. pom.xml dependencies · 3. ConfigReader · 4. PlaywrightFactory (ThreadLocal) · 5. BaseTest · 6. BasePage · 7. testng.xml · 8. Wait patterns · 9. JUnit 5 variant notes

Versions below are known-good at time of writing; tell the user to bump to the latest stable.

## 1. Project layout

```
src/
  main/java/com/example/
    config/ConfigReader.java
    factory/PlaywrightFactory.java
    pages/BasePage.java
    pages/<Feature>Page.java
    components/<Component>.java
  test/java/com/example/
    base/BaseTest.java
    tests/<feature>/<Feature>Test.java
    data/<Feature>Data.java
  test/resources/
    config.properties
    testng.xml
    allure.properties
```

## 2. pom.xml dependencies

```xml
<properties>
  <maven.compiler.source>17</maven.compiler.source>
  <maven.compiler.target>17</maven.compiler.target>
  <aspectj.version>1.9.22</aspectj.version>
  <allure.version>2.29.0</allure.version>
</properties>

<dependencies>
  <dependency>
    <groupId>com.microsoft.playwright</groupId>
    <artifactId>playwright</artifactId>
    <version>1.49.0</version>
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
    <version>${allure.version}</version>
  </dependency>
</dependencies>

<build>
  <plugins>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-surefire-plugin</artifactId>
      <version>3.2.5</version>
      <configuration>
        <suiteXmlFiles>
          <suiteXmlFile>src/test/resources/testng.xml</suiteXmlFile>
        </suiteXmlFiles>
        <argLine>
          -javaagent:"${settings.localRepository}/org/aspectj/aspectjweaver/${aspectj.version}/aspectjweaver-${aspectj.version}.jar"
        </argLine>
      </configuration>
      <dependencies>
        <dependency>
          <groupId>org.aspectj</groupId>
          <artifactId>aspectjweaver</artifactId>
          <version>${aspectj.version}</version>
        </dependency>
      </dependencies>
    </plugin>
  </plugins>
</build>
```

The AspectJ agent is what makes `@Step` on page methods show up in Allure.

## 3. ConfigReader

```java
package com.example.config;

import java.io.InputStream;
import java.util.Properties;

public final class ConfigReader {
    private static final Properties PROPS = new Properties();

    static {
        try (InputStream in = ConfigReader.class.getClassLoader()
                .getResourceAsStream("config.properties")) {
            if (in == null) throw new IllegalStateException("config.properties not found");
            PROPS.load(in);
        } catch (Exception e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    private ConfigReader() {}

    /** System property (-Dkey=value) wins over the file, so CI can override. */
    public static String get(String key) {
        return System.getProperty(key, PROPS.getProperty(key));
    }

    public static int getInt(String key) { return Integer.parseInt(get(key)); }
    public static boolean getBool(String key) { return Boolean.parseBoolean(get(key)); }
}
```

`config.properties`:
```
baseUrl=https://www.saucedemo.com
browser=chromium
headless=true
defaultTimeoutMs=10000
navigationTimeoutMs=30000
testIdAttribute=data-test
traceOnFailure=true
```

## 4. PlaywrightFactory (ThreadLocal sessions)

```java
package com.example.factory;

import com.example.config.ConfigReader;
import com.microsoft.playwright.*;

public final class PlaywrightFactory {

    private static final ThreadLocal<Playwright> PLAYWRIGHT = new ThreadLocal<>();
    private static final ThreadLocal<Browser> BROWSER = new ThreadLocal<>();
    private static final ThreadLocal<BrowserContext> CONTEXT = new ThreadLocal<>();
    private static final ThreadLocal<Page> PAGE = new ThreadLocal<>();

    private PlaywrightFactory() {}

    public static Page start() {
        Playwright pw = Playwright.create();
        pw.selectors().setTestIdAttribute(ConfigReader.get("testIdAttribute"));
        PLAYWRIGHT.set(pw);

        BrowserType.LaunchOptions launch = new BrowserType.LaunchOptions()
                .setHeadless(ConfigReader.getBool("headless"));
        Browser browser = switch (ConfigReader.get("browser")) {
            case "firefox" -> pw.firefox().launch(launch);
            case "webkit"  -> pw.webkit().launch(launch);
            default        -> pw.chromium().launch(launch);
        };
        BROWSER.set(browser);

        BrowserContext ctx = browser.newContext(new Browser.NewContextOptions()
                .setBaseURL(ConfigReader.get("baseUrl"))
                .setViewportSize(1440, 900));
        ctx.setDefaultTimeout(ConfigReader.getInt("defaultTimeoutMs"));
        ctx.setDefaultNavigationTimeout(ConfigReader.getInt("navigationTimeoutMs"));
        if (ConfigReader.getBool("traceOnFailure")) {
            ctx.tracing().start(new Tracing.StartOptions()
                    .setScreenshots(true).setSnapshots(true).setSources(true));
        }
        CONTEXT.set(ctx);

        Page page = ctx.newPage();
        PAGE.set(page);
        return page;
    }

    public static Page page() { return PAGE.get(); }
    public static BrowserContext context() { return CONTEXT.get(); }

    public static void stop() {
        // Close in reverse order and always clear ThreadLocals to avoid leaks in pooled threads.
        try { if (CONTEXT.get() != null) CONTEXT.get().close(); } finally { CONTEXT.remove(); PAGE.remove(); }
        try { if (BROWSER.get() != null) BROWSER.get().close(); } finally { BROWSER.remove(); }
        try { if (PLAYWRIGHT.get() != null) PLAYWRIGHT.get().close(); } finally { PLAYWRIGHT.remove(); }
    }
}
```

One `Playwright` per thread is deliberate: the Playwright Java object is not thread-safe.

## 5. BaseTest

```java
package com.example.base;

import com.example.config.ConfigReader;
import com.example.factory.PlaywrightFactory;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Tracing;
import io.qameta.allure.Allure;
import org.testng.ITestResult;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;

import java.io.ByteArrayInputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public abstract class BaseTest {

    protected Page page() { return PlaywrightFactory.page(); }

    @BeforeMethod(alwaysRun = true)
    public void setUp() {
        PlaywrightFactory.start();
    }

    @AfterMethod(alwaysRun = true)
    public void tearDown(ITestResult result) {
        try {
            if (!result.isSuccess() && page() != null) {
                Allure.addAttachment("Screenshot on failure", "image/png",
                        new ByteArrayInputStream(page().screenshot(new Page.ScreenshotOptions().setFullPage(true))),
                        "png");
                Allure.addAttachment("URL on failure", page().url());
            }
            if (ConfigReader.getBool("traceOnFailure") && PlaywrightFactory.context() != null) {
                if (!result.isSuccess()) {
                    Path trace = Paths.get("target/traces",
                            result.getMethod().getMethodName() + "-" + Thread.currentThread().getId() + ".zip");
                    PlaywrightFactory.context().tracing().stop(new Tracing.StopOptions().setPath(trace));
                    Allure.addAttachment("Playwright trace (open with: npx playwright show-trace)",
                            "application/zip", Files.newInputStream(trace), "zip");
                } else {
                    PlaywrightFactory.context().tracing().stop();
                }
            }
        } catch (Exception e) {
            System.err.println("Failure-artifact capture failed: " + e.getMessage());
        } finally {
            PlaywrightFactory.stop();
        }
    }
}
```

## 6. BasePage

```java
package com.example.pages;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Response;

import java.util.function.Predicate;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

public abstract class BasePage {
    protected final Page page;

    protected BasePage(Page page) {
        this.page = page;
    }

    /** Run an action and wait for the matching network response, instead of sleeping. */
    protected Response clickAndWaitForResponse(Locator target, Predicate<Response> matcher) {
        return page.waitForResponse(matcher, target::click);
    }

    protected void waitUntilHidden(Locator loader) {
        assertThat(loader).isHidden();
    }

    /** Pages override this with a stable "page is ready" signal. */
    public abstract BasePage waitUntilLoaded();
}
```

## 7. testng.xml (parallel)

```xml
<!DOCTYPE suite SYSTEM "https://testng.org/testng-1.0.dtd">
<suite name="Regression" parallel="methods" thread-count="4">
  <test name="Web">
    <packages>
      <package name="com.example.tests.*"/>
    </packages>
  </test>
</suite>
```

`parallel="methods"` only works because every session object is ThreadLocal and created per method.

## 8. Wait patterns

| Situation | Use | Avoid |
|---|---|---|
| Element should appear | `assertThat(loc).isVisible()` | `Thread.sleep`, `waitForTimeout` |
| Text updates async (price, count) | `assertThat(loc).hasText("$1,299")` / `containsText` | reading `textContent()` then asserting |
| List loads | `assertThat(items).hasCount(6)` | `items.count()` immediately |
| Action triggers API | `page.waitForResponse(r -> r.url().contains("/api/cart") && r.ok(), () -> btn.click())` | clicking then sleeping |
| Spinner | `assertThat(spinner).isHidden()` | polling loops |
| Navigation | `page.waitForURL("**/checkout-step-one.html")` or `assertThat(page).hasURL(...)` | checking `page.url()` right after click |
| Element must exist but may be offscreen | `loc.waitFor(new Locator.WaitForOptions().setState(WaitForSelectorState.ATTACHED))` | |
| Custom polling (non-UI condition) | loop with deadline from config + `page.waitForTimeout` only inside a documented helper, or better, `waitForFunction` | ad-hoc sleeps in tests |

Imports: `import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;`, `com.microsoft.playwright.options.WaitForSelectorState`, `com.microsoft.playwright.options.AriaRole`.

Custom assertion timeout: `assertThat(loc).isVisible(new LocatorAssertions.IsVisibleOptions().setTimeout(ConfigReader.getInt("longTimeoutMs")))`.

## 9. JUnit 5 variant notes

If the user's project uses JUnit 5: replace `@BeforeMethod/@AfterMethod` with `@BeforeEach/@AfterEach`, use `allure-junit5`, detect failure via a `TestWatcher` extension (or `AfterTestExecutionCallback`) instead of `ITestResult`, `@DataProvider` → `@ParameterizedTest` + `@MethodSource`, and enable parallelism in `junit-platform.properties` (`junit.jupiter.execution.parallel.enabled=true`, `mode.default=concurrent`). ThreadLocal design is unchanged.
