# Worked example: saucedemo.com

Public demo app, `testIdAttribute=data-test`. Shows the expected input → output shape.

## Input (manual test cases)

| ID | Title | Priority | Pre-condition | Steps | Expected |
|---|---|---|---|---|---|
| TC-001 | Valid login | P0 | On login page | 1. Enter standard_user / secret_sauce 2. Click Login | Products page shown with title "Products" |
| TC-002 | Locked user login | P1 | On login page | 1. Enter locked_out_user / secret_sauce 2. Click Login | Error "Sorry, this user has been locked out." shown; stays on login page |
| TC-003 | Add item to cart | P0 | Logged in | 1. Click "Add to cart" on Sauce Labs Backpack 2. Open cart | Cart badge shows 1; backpack listed in cart |
| TC-004 | Product image looks right | P2 | Logged in | 1. View inventory | Images look correct |

## Output

### `src/main/java/com/example/pages/LoginPage.java`

```java
package com.example.pages;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import io.qameta.allure.Step;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

public class LoginPage extends BasePage {
    private final Locator username;
    private final Locator password;
    private final Locator loginButton;
    private final Locator error;

    public LoginPage(Page page) {
        super(page);
        this.username = page.getByTestId("username");
        this.password = page.getByTestId("password");
        this.loginButton = page.getByTestId("login-button");
        this.error = page.getByTestId("error");
    }

    @Step("Open login page")
    public LoginPage open() {
        page.navigate("/");
        return waitUntilLoaded();
    }

    @Override
    public LoginPage waitUntilLoaded() {
        assertThat(loginButton).isVisible();
        return this;
    }

    @Step("Log in as {user}")
    public InventoryPage loginAs(String user, String pass) {
        submit(user, pass);
        return new InventoryPage(page).waitUntilLoaded();
    }

    @Step("Attempt login as {user} (expecting failure)")
    public LoginPage attemptLogin(String user, String pass) {
        submit(user, pass);
        return this;
    }

    public Locator errorMessage() { return error; }
    public Locator loginButton() { return loginButton; }

    private void submit(String user, String pass) {
        username.fill(user);
        password.fill(pass);
        loginButton.click();
    }
}
```

### `src/main/java/com/example/pages/InventoryPage.java`

```java
package com.example.pages;

import com.example.components.Header;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.AriaRole;
import io.qameta.allure.Step;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

public class InventoryPage extends BasePage {
    private final Locator title;
    private final Locator items;
    public final Header header;

    public InventoryPage(Page page) {
        super(page);
        this.title = page.getByTestId("title");
        this.items = page.getByTestId("inventory-item");
        this.header = new Header(page);
    }

    @Override
    public InventoryPage waitUntilLoaded() {
        assertThat(page).hasURL(java.util.regex.Pattern.compile(".*/inventory\\.html"));
        assertThat(title).isVisible();
        return this;
    }

    @Step("Add '{productName}' to cart")
    public InventoryPage addToCart(String productName) {
        items.filter(new Locator.FilterOptions().setHasText(productName))
             .getByRole(AriaRole.BUTTON, new Locator.GetByRoleOptions().setName("Add to cart"))
             .click();
        return this;
    }

    public Locator title() { return title; }
}
```

### `src/main/java/com/example/components/Header.java`

```java
package com.example.components;

import com.example.pages.CartPage;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import io.qameta.allure.Step;

public class Header {
    private final Page page;
    private final Locator cartLink;
    private final Locator cartBadge;

    public Header(Page page) {
        this.page = page;
        this.cartLink = page.getByTestId("shopping-cart-link");
        this.cartBadge = page.getByTestId("shopping-cart-badge");
    }

    @Step("Open cart")
    public CartPage openCart() {
        cartLink.click();
        return new CartPage(page).waitUntilLoaded();
    }

    public Locator cartBadge() { return cartBadge; }
}
```

### `src/main/java/com/example/pages/CartPage.java`

```java
package com.example.pages;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

public class CartPage extends BasePage {
    private final Locator itemNames;

    public CartPage(Page page) {
        super(page);
        this.itemNames = page.getByTestId("inventory-item-name");
    }

    @Override
    public CartPage waitUntilLoaded() {
        assertThat(page).hasURL(java.util.regex.Pattern.compile(".*/cart\\.html"));
        return this;
    }

    public Locator itemNames() { return itemNames; }
}
```

### `src/test/java/com/example/data/Users.java`

```java
package com.example.data;

public final class Users {
    private Users() {}
    public static final String STANDARD = "standard_user";
    public static final String LOCKED = "locked_out_user";
    public static final String PASSWORD = "secret_sauce"; // public demo credential
}
```

### `src/test/java/com/example/tests/auth/LoginTest.java`

```java
package com.example.tests.auth;

import com.example.base.BaseTest;
import com.example.data.Users;
import com.example.pages.LoginPage;
import io.qameta.allure.*;
import org.testng.annotations.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@Epic("Web Store")
@Feature("Authentication")
public class LoginTest extends BaseTest {

    @Test(description = "TC-001: Valid login")
    @TmsLink("TC-001")
    @Story("Login")
    @Severity(SeverityLevel.BLOCKER)
    public void shouldLandOnProductsAfterValidLogin() {
        var inventory = new LoginPage(page()).open()
                .loginAs(Users.STANDARD, Users.PASSWORD);

        assertThat(inventory.title()).hasText("Products");
    }

    @Test(description = "TC-002: Locked user login")
    @TmsLink("TC-002")
    @Story("Login")
    @Severity(SeverityLevel.NORMAL)
    public void shouldShowErrorForLockedUser() {
        var login = new LoginPage(page()).open()
                .attemptLogin(Users.LOCKED, Users.PASSWORD);

        assertThat(login.errorMessage()).containsText("Sorry, this user has been locked out.");
        assertThat(login.loginButton()).isVisible(); // still on login page
    }
}
```

### `src/test/java/com/example/tests/cart/CartTest.java`

```java
package com.example.tests.cart;

import com.example.base.BaseTest;
import com.example.data.Users;
import com.example.pages.LoginPage;
import io.qameta.allure.*;
import org.testng.annotations.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@Epic("Web Store")
@Feature("Cart")
public class CartTest extends BaseTest {

    private static final String BACKPACK = "Sauce Labs Backpack";

    @Test(description = "TC-003: Add item to cart")
    @TmsLink("TC-003")
    @Story("Add to cart")
    @Severity(SeverityLevel.BLOCKER)
    public void shouldShowAddedItemInCart() {
        var inventory = new LoginPage(page()).open()
                .loginAs(Users.STANDARD, Users.PASSWORD)
                .addToCart(BACKPACK);

        assertThat(inventory.header.cartBadge()).hasText("1");

        var cart = inventory.header.openCart();
        assertThat(cart.itemNames()).hasText(BACKPACK);
    }
}
```

### Traceability

| Case ID | Test method | Steps automated | Notes |
|---|---|---|---|
| TC-001 | LoginTest.shouldLandOnProductsAfterValidLogin | 2/2 | |
| TC-002 | LoginTest.shouldShowErrorForLockedUser | 2/2 | "stays on login page" asserted via login button visibility |
| TC-003 | CartTest.shouldShowAddedItemInCart | 2/2 | Precondition "logged in" done via UI; swap for session cookie/API if available |

### Not automated

- **TC-004**: "Images look correct" is a visual judgement. Option: Playwright screenshot comparison isn't built into Java assertions; use a visual tool (e.g. Applitools/Percy) or assert each `img` has a non-empty `src` and loaded `naturalWidth > 0` via `evaluate`.

### Needs verification

0 `TODO-VERIFY` locators (all taken from the app's `data-test` attributes).
