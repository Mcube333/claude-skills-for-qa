# Worked example: Sauce Labs sample app (Swag Labs mobile)

Public app: github.com/saucelabs/sample-app-mobile (Android .apk and iOS .app in its releases). Elements expose `test-*` accessibility ids on both platforms. Shows expected output shape, including how unverified locators are flagged.

## Input

| ID | Title | Priority | Platform | Steps | Expected |
|---|---|---|---|---|---|
| TC-M01 | Valid login | P0 | Both | 1. Enter standard_user / secret_sauce 2. Tap LOGIN | Products screen shown |
| TC-M02 | Locked user | P1 | Both | 1. Enter locked_out_user / secret_sauce 2. Tap LOGIN | Error "Sorry, this user has been locked out." |
| TC-M03 | Add to cart | P0 | Both | Pre: logged in. 1. Tap ADD TO CART on first product | Cart badge shows 1 |

## Output

### `src/main/java/com/example/screens/LoginScreen.java`

```java
package com.example.screens;

import io.appium.java_client.AppiumDriver;
import io.appium.java_client.pagefactory.AndroidFindBy;
import io.appium.java_client.pagefactory.iOSXCUITFindBy;
import io.qameta.allure.Step;
import org.openqa.selenium.WebElement;

public class LoginScreen extends BaseScreen {

    @AndroidFindBy(accessibility = "test-Username")
    @iOSXCUITFindBy(accessibility = "test-Username")
    private WebElement username;

    @AndroidFindBy(accessibility = "test-Password")
    @iOSXCUITFindBy(accessibility = "test-Password")
    private WebElement password;

    @AndroidFindBy(accessibility = "test-LOGIN")
    @iOSXCUITFindBy(accessibility = "test-LOGIN")
    private WebElement loginButton;

    @AndroidFindBy(xpath = "//*[@content-desc='test-Error message']/android.widget.TextView") // child has no a11y id
    @iOSXCUITFindBy(accessibility = "test-Error message") // TODO-VERIFY locator
    private WebElement errorText;

    public LoginScreen(AppiumDriver driver) { super(driver); }

    @Override
    public LoginScreen waitUntilLoaded() {
        visible(loginButton);
        return this;
    }

    @Step("Log in as {user}")
    public ProductsScreen loginAs(String user, String pass) {
        submit(user, pass);
        return new ProductsScreen(driver).waitUntilLoaded();
    }

    @Step("Attempt login as {user} (expecting failure)")
    public LoginScreen attemptLogin(String user, String pass) {
        submit(user, pass);
        return this;
    }

    public String errorMessage() { return textOf(errorText); }

    private void submit(String user, String pass) {
        type(username, user);
        type(password, pass);
        tap(loginButton);
    }
}
```

### `src/main/java/com/example/screens/ProductsScreen.java`

```java
package com.example.screens;

import io.appium.java_client.AppiumDriver;
import io.appium.java_client.pagefactory.AndroidFindBy;
import io.appium.java_client.pagefactory.iOSXCUITFindBy;
import io.qameta.allure.Step;
import org.openqa.selenium.WebElement;

import java.util.List;

public class ProductsScreen extends BaseScreen {

    @AndroidFindBy(accessibility = "test-PRODUCTS")   // TODO-VERIFY locator
    @iOSXCUITFindBy(accessibility = "test-PRODUCTS")  // TODO-VERIFY locator
    private WebElement productsContainer;

    @AndroidFindBy(accessibility = "test-ADD TO CART")
    @iOSXCUITFindBy(accessibility = "test-ADD TO CART")
    private List<WebElement> addToCartButtons;

    @AndroidFindBy(xpath = "//*[@content-desc='test-Cart']//android.widget.TextView") // TODO-VERIFY locator
    @iOSXCUITFindBy(iOSNsPredicate = "name == 'test-Cart'")                            // TODO-VERIFY locator
    private WebElement cartBadge;

    public ProductsScreen(AppiumDriver driver) { super(driver); }

    @Override
    public ProductsScreen waitUntilLoaded() {
        visible(productsContainer);
        return this;
    }

    @Step("Add first product to cart")
    public ProductsScreen addFirstProductToCart() {
        tap(addToCartButtons.get(0));
        return this;
    }

    public boolean isLoaded() { return isDisplayed(productsContainer); }
    public String cartCount() { return textOf(cartBadge); }
}
```

### `src/test/java/com/example/tests/auth/LoginTest.java`

```java
package com.example.tests.auth;

import com.example.base.BaseTest;
import com.example.screens.LoginScreen;
import io.qameta.allure.*;
import org.testng.annotations.Test;

import static org.testng.Assert.assertEquals;
import static org.testng.Assert.assertTrue;

@Epic("Mobile Store")
@Feature("Authentication")
public class LoginTest extends BaseTest {

    private static final String PASSWORD = "secret_sauce"; // public demo credential

    @Test(description = "TC-M01: Valid login")
    @TmsLink("TC-M01") @Story("Login") @Severity(SeverityLevel.BLOCKER)
    public void shouldOpenProductsAfterValidLogin() {
        var products = new LoginScreen(driver()).waitUntilLoaded().loginAs("standard_user", PASSWORD);
        assertTrue(products.isLoaded(), "Products screen not shown after login");
    }

    @Test(description = "TC-M02: Locked user")
    @TmsLink("TC-M02") @Story("Login") @Severity(SeverityLevel.NORMAL)
    public void shouldShowErrorForLockedUser() {
        String error = new LoginScreen(driver()).waitUntilLoaded()
                .attemptLogin("locked_out_user", PASSWORD)
                .errorMessage();
        assertEquals(error, "Sorry, this user has been locked out.");
    }

    @Test(description = "TC-M03: Add to cart")
    @TmsLink("TC-M03") @Story("Cart") @Severity(SeverityLevel.BLOCKER)
    public void shouldIncrementCartBadge() {
        var products = new LoginScreen(driver()).waitUntilLoaded()
                .loginAs("standard_user", PASSWORD)
                .addFirstProductToCart();
        assertEquals(products.cartCount(), "1", "Cart badge count");
    }
}
```

### Traceability

| Case ID | Test method | Steps | Notes |
|---|---|---|---|
| TC-M01 | LoginTest.shouldOpenProductsAfterValidLogin | 2/2 | |
| TC-M02 | LoginTest.shouldShowErrorForLockedUser | 2/2 | |
| TC-M03 | LoginTest.shouldIncrementCartBadge | 1/1 | Login precondition via UI (app has no deep link for it) |

### Not automated
None.

### Needs verification
5 `TODO-VERIFY` locators: products container (both), cart badge (both), iOS error text. Confirm in Appium Inspector. Assumed capabilities: `android.appPackage=com.swaglabsmobileapp`, `android.appActivity=.MainActivity`.
