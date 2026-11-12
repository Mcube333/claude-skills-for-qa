# REST Assured framework scaffold

Contents: 1. Layout · 2. pom.xml · 3. config · 4. SpecFactory · 5. Auth · 6. Client class · 7. Payloads (records + builders) · 8. BaseApiTest · 9. Test patterns · 10. Schema validation

Versions are known-good at time of writing; tell the user to bump to latest stable.

## 1. Layout

```
src/main/java/com/example/api/
  config/ConfigReader.java
  core/SpecFactory.java
  auth/AuthClient.java
  clients/<Resource>Client.java
  models/<Resource>.java          (records)
src/test/java/com/example/api/
  base/BaseApiTest.java
  data/<Resource>Data.java        (builders, data providers)
  tests/<resource>/<Resource>Test.java
src/test/resources/
  config.properties
  schemas/<resource>/<name>.json
  testng.xml
```

## 2. pom.xml

```xml
<properties>
  <maven.compiler.source>17</maven.compiler.source>
  <maven.compiler.target>17</maven.compiler.target>
  <restassured.version>5.5.0</restassured.version>
  <allure.version>2.29.0</allure.version>
</properties>
<dependencies>
  <dependency>
    <groupId>io.rest-assured</groupId>
    <artifactId>rest-assured</artifactId>
    <version>${restassured.version}</version>
  </dependency>
  <dependency>
    <groupId>io.rest-assured</groupId>
    <artifactId>json-schema-validator</artifactId>
    <version>${restassured.version}</version>
  </dependency>
  <dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
    <version>2.17.2</version>
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
  <dependency>
    <groupId>io.qameta.allure</groupId>
    <artifactId>allure-rest-assured</artifactId>
    <version>${allure.version}</version>
  </dependency>
</dependencies>
<!-- surefire with testng.xml + aspectjweaver javaagent, as in any Allure TestNG project -->
```

## 3. config.properties

```
baseUrl=https://api.example.com
auth.username=${API_USER}
auth.password=${API_PASSWORD}
maxResponseMs=3000
```

ConfigReader: load from classpath; `-Dkey=value` and environment variables override; resolve `${ENV}` placeholders from `System.getenv`. Secrets live in CI secrets / local env, never in the repo.

```java
public static String get(String key) {
    String v = System.getProperty(key, PROPS.getProperty(key));
    if (v != null && v.startsWith("${") && v.endsWith("}")) {
        String env = v.substring(2, v.length() - 1);
        v = System.getenv(env);
        if (v == null) throw new IllegalStateException("Missing env var " + env + " for config key " + key);
    }
    return v;
}
```

## 4. SpecFactory

```java
package com.example.api.core;

import com.example.api.config.ConfigReader;
import io.qameta.allure.restassured.AllureRestAssured;
import io.restassured.builder.RequestSpecBuilder;
import io.restassured.builder.ResponseSpecBuilder;
import io.restassured.http.ContentType;
import io.restassured.specification.RequestSpecification;
import io.restassured.specification.ResponseSpecification;

import java.util.concurrent.TimeUnit;

import static org.hamcrest.Matchers.lessThan;

/** Builds fresh spec instances; never touches RestAssured static fields per test. */
public final class SpecFactory {
    private SpecFactory() {}

    public static RequestSpecification base() {
        return new RequestSpecBuilder()
                .setBaseUri(ConfigReader.get("baseUrl"))
                .setContentType(ContentType.JSON)
                .setAccept(ContentType.JSON)
                .addFilter(new AllureRestAssured())     // request/response attached to the Allure step
                .build();
    }

    public static RequestSpecification authed(String token) {
        return new RequestSpecBuilder()
                .addRequestSpecification(base())
                .addHeader("Authorization", "Bearer " + token)
                .build();
    }

    /** Loose guard against hangs, not a performance test. */
    public static ResponseSpecification withinSla() {
        return new ResponseSpecBuilder()
                .expectResponseTime(lessThan((long) Integer.parseInt(ConfigReader.get("maxResponseMs"))),
                        TimeUnit.MILLISECONDS)
                .build();
    }
}
```

Adapt `authed` to the API's scheme: cookie (`addCookie("token", t)`), API key header, or basic (`setAuth(RestAssured.preemptive().basic(u, p))`).

## 5. Auth

```java
package com.example.api.auth;

import com.example.api.config.ConfigReader;
import com.example.api.core.SpecFactory;

import java.util.Map;

import static io.restassured.RestAssured.given;

public final class AuthClient {
    private static volatile String cachedToken;

    private AuthClient() {}

    /** Thread-safe lazy token: fetched once, read-only afterwards. */
    public static String token() {
        if (cachedToken == null) {
            synchronized (AuthClient.class) {
                if (cachedToken == null) {
                    cachedToken = given().spec(SpecFactory.base())
                            .body(Map.of("username", ConfigReader.get("auth.username"),
                                         "password", ConfigReader.get("auth.password")))
                            .post("/auth/login")                 // adapt path
                            .then().statusCode(200)
                            .extract().path("token");          // adapt field
                }
            }
        }
        return cachedToken;
    }
}
```

If tokens expire during a run, add expiry tracking or fetch per test class.

## 6. Client class

```java
package com.example.api.clients;

import com.example.api.core.SpecFactory;
import com.example.api.models.Item;
import io.qameta.allure.Step;
import io.restassured.response.Response;
import io.restassured.specification.RequestSpecification;

import static io.restassured.RestAssured.given;

public class ItemClient {
    private static final String ITEMS = "/items";
    private static final String ITEM = "/items/{id}";
    private final RequestSpecification spec;

    public ItemClient(RequestSpecification spec) { this.spec = spec; }

    @Step("POST /items")
    public Response create(Object body) {          // Object: lets negatives pass Maps/raw JSON
        return given().spec(spec).body(body).post(ITEMS);
    }

    @Step("GET /items/{id}")
    public Response get(Object id) {
        return given().spec(spec).pathParam("id", id).get(ITEM);
    }

    @Step("DELETE /items/{id}")
    public Response delete(Object id) {
        return given().spec(spec).pathParam("id", id).delete(ITEM);
    }
}
```

## 7. Payloads

Records for valid payloads (Jackson 2.12+ handles them), a data class with builders and generated values:

```java
package com.example.api.models;

public record Item(String name, Integer quantity, String category) {
    public Item withName(String v) { return new Item(v, quantity, category); }
    public Item withQuantity(Integer v) { return new Item(name, v, category); }
}
```

```java
package com.example.api.data;

import com.example.api.models.Item;
import java.util.*;

public final class ItemData {
    private ItemData() {}

    public static Item valid() {
        return new Item("item-" + UUID.randomUUID().toString().substring(0, 8), 2, "BOOKS");
    }

    /** Invalid shapes need a Map: a record can't omit a field or hold a wrong type. */
    public static Map<String, Object> validAsMap() {
        Map<String, Object> m = new LinkedHashMap<>();
        Item i = valid();
        m.put("name", i.name()); m.put("quantity", i.quantity()); m.put("category", i.category());
        return m;
    }

    public static Map<String, Object> without(String field) {
        Map<String, Object> m = validAsMap(); m.remove(field); return m;
    }

    public static Map<String, Object> with(String field, Object value) {
        Map<String, Object> m = validAsMap(); m.put(field, value); return m;
    }
}
```

## 8. BaseApiTest

```java
package com.example.api.base;

import io.restassured.RestAssured;
import org.testng.annotations.BeforeSuite;

public abstract class BaseApiTest {
    @BeforeSuite(alwaysRun = true)
    public void globalSetup() {
        // Set once before any test; read-only afterwards, so safe for parallel runs.
        RestAssured.enableLoggingOfRequestAndResponseIfValidationFails();
    }
}
```

## 9. Test patterns

```java
@Test(description = "Create item returns 201 and echoes payload")
@Story("Create") @Severity(SeverityLevel.CRITICAL)
public void shouldCreateItem() {
    Item payload = ItemData.valid();
    String id = null;
    try {
        id = client.create(payload).then()
                .spec(SpecFactory.withinSla())
                .statusCode(201)
                .contentType(ContentType.JSON)
                .body(matchesJsonSchemaInClasspath("schemas/items/item.json"))
                .body("name", equalTo(payload.name()))
                .body("quantity", equalTo(payload.quantity()))
                .extract().path("id");
    } finally {
        if (id != null) client.delete(id);   // cleanup even if assertions fail
    }
}

@DataProvider(name = "missingRequired", parallel = true)
public Object[][] missingRequired() {
    return new Object[][] { {"missing name", "name"}, {"missing quantity", "quantity"} };
}

@Test(dataProvider = "missingRequired")
@Story("Create - validation") @Severity(SeverityLevel.NORMAL)
public void shouldRejectMissingRequiredField(String label, String field) {
    client.create(ItemData.without(field)).then()
            .statusCode(anyOf(is(400), is(422)))      // undocumented exact code → flag in output
            .body(matchesJsonSchemaInClasspath("schemas/common/error.json"));
}

@Test(description = "Unauthenticated create is rejected")
public void shouldRejectWithoutAuth() {
    new ItemClient(SpecFactory.base()).create(ItemData.valid()).then().statusCode(401);
}
```

Static imports: `io.restassured.module.jsv.JsonSchemaValidator.matchesJsonSchemaInClasspath`, `org.hamcrest.Matchers.*`.

## 10. Schema validation

```json
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "title": "Item",
  "type": "object",
  "required": ["id", "name", "quantity"],
  "properties": {
    "id": { "type": "string" },
    "name": { "type": "string", "minLength": 1 },
    "quantity": { "type": "integer", "minimum": 1 },
    "category": { "type": ["string", "null"], "enum": ["BOOKS", "TOYS", null] }
  }
}
```

Validate every documented response with a body, including error responses (a shared `schemas/common/error.json` is common).
