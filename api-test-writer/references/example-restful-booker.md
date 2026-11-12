# Worked example: restful-booker (public practice API)

Base URL `https://restful-booker.herokuapp.com`. Public demo creds `admin` / `password123` (still read from config, to model good practice). It has deliberate quirks, which make it a good example of asserting **actual documented behaviour** and flagging oddities instead of "fixing" expectations:

- `POST /booking` returns **200** (not 201).
- `POST /auth` with bad credentials returns **200** with `{"reason":"Bad credentials"}`.
- `PUT`/`PATCH`/`DELETE` need `Cookie: token=<token>`; missing/invalid token → **403**.
- `DELETE` returns **201**.
- Missing required field on create → **500** (a real bug-like behaviour, worth a test that documents it).

## Input (cURL)

```bash
curl -X POST https://restful-booker.herokuapp.com/booking \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -d '{"firstname":"Jim","lastname":"Brown","totalprice":111,"depositpaid":true,
       "bookingdates":{"checkin":"2018-01-01","checkout":"2019-01-01"},"additionalneeds":"Breakfast"}'
```
Sample response:
```json
{"bookingid":1,"booking":{"firstname":"Jim","lastname":"Brown","totalprice":111,"depositpaid":true,
 "bookingdates":{"checkin":"2018-01-01","checkout":"2019-01-01"},"additionalneeds":"Breakfast"}}
```
User also asked for get/delete coverage.

## Output

### Coverage matrix

| Endpoint | Positive | Contract | Auth | Validation | Not found | Flow |
|---|---|---|---|---|---|---|
| POST /booking | ✓ | ✓ (inferred) | ✗ (public) | ✓ (documents 500) | ✗ | ✓ |
| GET /booking/{id} | ✓ | ✓ (inferred) | ✗ (public) | ✗ | ✓ | ✓ |
| DELETE /booking/{id} | ✓ | ✗ (no body) | ✓ | ✗ | gap | ✓ |

### `src/main/java/com/example/api/models/Booking.java`

```java
package com.example.api.models;

import com.fasterxml.jackson.annotation.JsonInclude;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record Booking(String firstname, String lastname, Integer totalprice, Boolean depositpaid,
                      BookingDates bookingdates, String additionalneeds) {
    public record BookingDates(String checkin, String checkout) {}
}
```

### `src/main/java/com/example/api/clients/BookingClient.java`

```java
package com.example.api.clients;

import io.qameta.allure.Step;
import io.restassured.response.Response;
import io.restassured.specification.RequestSpecification;

import static io.restassured.RestAssured.given;

public class BookingClient {
    private final RequestSpecification spec;

    public BookingClient(RequestSpecification spec) { this.spec = spec; }

    @Step("POST /booking")
    public Response create(Object body) { return given().spec(spec).body(body).post("/booking"); }

    @Step("GET /booking/{id}")
    public Response get(Object id) { return given().spec(spec).pathParam("id", id).get("/booking/{id}"); }

    @Step("DELETE /booking/{id}")
    public Response delete(Object id, String token) {
        var req = given().spec(spec).pathParam("id", id);
        if (token != null) req = req.cookie("token", token);
        return req.delete("/booking/{id}");
    }
}
```

### `src/main/java/com/example/api/auth/AuthClient.java` (adapted)

```java
// Same lazy, thread-safe pattern as the scaffold; adapted for restful-booker:
cachedToken = given().spec(SpecFactory.base())
        .body(Map.of("username", ConfigReader.get("auth.username"),
                     "password", ConfigReader.get("auth.password")))
        .post("/auth")
        .then().statusCode(200)
        .body("token", notNullValue())   // API returns 200 + "reason" on bad creds, so check the token exists
        .extract().path("token");
```

### `src/test/java/com/example/api/data/BookingData.java`

```java
package com.example.api.data;

import com.example.api.models.Booking;
import com.example.api.models.Booking.BookingDates;

import java.time.LocalDate;
import java.util.*;

public final class BookingData {
    private BookingData() {}

    public static Booking valid() {
        LocalDate in = LocalDate.now().plusDays(10);
        return new Booking("Test", "User-" + UUID.randomUUID().toString().substring(0, 6), 150, true,
                new BookingDates(in.toString(), in.plusDays(3).toString()), "Breakfast");
    }

    public static Map<String, Object> without(String field) {
        Booking b = valid();
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("firstname", b.firstname()); m.put("lastname", b.lastname());
        m.put("totalprice", b.totalprice()); m.put("depositpaid", b.depositpaid());
        m.put("bookingdates", Map.of("checkin", b.bookingdates().checkin(), "checkout", b.bookingdates().checkout()));
        m.remove(field);
        return m;
    }
}
```

### `src/test/resources/schemas/booking/create-booking.json`

```json
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "description": "Inferred from one sample - verify against the API contract",
  "type": "object",
  "required": ["bookingid", "booking"],
  "properties": {
    "bookingid": { "type": "integer" },
    "booking": { "$ref": "#/definitions/booking" }
  },
  "definitions": {
    "booking": {
      "type": "object",
      "required": ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates"],
      "properties": {
        "firstname": { "type": "string" },
        "lastname": { "type": "string" },
        "totalprice": { "type": "integer" },
        "depositpaid": { "type": "boolean" },
        "bookingdates": {
          "type": "object",
          "required": ["checkin", "checkout"],
          "properties": {
            "checkin": { "type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$" },
            "checkout": { "type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$" }
          }
        },
        "additionalneeds": { "type": "string" }
      }
    }
  }
}
```

`get-booking.json` = the `booking` definition as the root object.

### `src/test/java/com/example/api/tests/booking/BookingTest.java`

```java
package com.example.api.tests.booking;

import com.example.api.auth.AuthClient;
import com.example.api.base.BaseApiTest;
import com.example.api.clients.BookingClient;
import com.example.api.core.SpecFactory;
import com.example.api.data.BookingData;
import com.example.api.models.Booking;
import io.qameta.allure.*;
import org.testng.annotations.DataProvider;
import org.testng.annotations.Test;

import static io.restassured.module.jsv.JsonSchemaValidator.matchesJsonSchemaInClasspath;
import static org.hamcrest.Matchers.*;

@Epic("Booking API")
@Feature("Bookings")
public class BookingTest extends BaseApiTest {

    private final BookingClient client = new BookingClient(SpecFactory.base());

    @Test(description = "Create booking echoes payload and matches schema")
    @Story("Create") @Severity(SeverityLevel.CRITICAL)
    public void shouldCreateBooking() {
        Booking payload = BookingData.valid();
        Integer id = null;
        try {
            id = client.create(payload).then()
                    .spec(SpecFactory.withinSla())
                    .statusCode(200)                                   // API quirk: 200, not 201
                    .body(matchesJsonSchemaInClasspath("schemas/booking/create-booking.json"))
                    .body("booking.firstname", equalTo(payload.firstname()))
                    .body("booking.lastname", equalTo(payload.lastname()))
                    .body("booking.totalprice", equalTo(payload.totalprice()))
                    .body("booking.bookingdates.checkin", equalTo(payload.bookingdates().checkin()))
                    .extract().path("bookingid");
        } finally {
            if (id != null) client.delete(id, AuthClient.token());
        }
    }

    @Test(description = "Full lifecycle: create, read, delete, read-404")
    @Story("Flow") @Severity(SeverityLevel.CRITICAL)
    public void shouldCompleteBookingLifecycle() {
        Booking payload = BookingData.valid();
        int id = client.create(payload).then().statusCode(200).extract().path("bookingid");

        client.get(id).then()
                .statusCode(200)
                .body(matchesJsonSchemaInClasspath("schemas/booking/get-booking.json"))
                .body("lastname", equalTo(payload.lastname()));

        client.delete(id, AuthClient.token()).then().statusCode(201);      // API quirk: 201 on delete
        client.get(id).then().statusCode(404);
    }

    @Test(description = "Delete without token is forbidden")
    @Story("Delete - auth") @Severity(SeverityLevel.CRITICAL)
    public void shouldRejectDeleteWithoutToken() {
        int id = client.create(BookingData.valid()).then().statusCode(200).extract().path("bookingid");
        try {
            client.delete(id, null).then().statusCode(403);
            client.delete(id, "invalid-token").then().statusCode(403);
        } finally {
            client.delete(id, AuthClient.token());
        }
    }

    @Test(description = "Unknown booking id returns 404")
    @Story("Read") @Severity(SeverityLevel.NORMAL)
    public void shouldReturn404ForUnknownBooking() {
        client.get(Integer.MAX_VALUE).then().statusCode(404);
    }

    @DataProvider(name = "missingRequired", parallel = true)
    public Object[][] missingRequired() {
        return new Object[][] { {"firstname"}, {"lastname"}, {"totalprice"}, {"depositpaid"}, {"bookingdates"} };
    }

    @Test(dataProvider = "missingRequired", description = "Missing required field is rejected")
    @Story("Create - validation") @Severity(SeverityLevel.NORMAL)
    @Issue("API returns 500 instead of 4xx for missing fields")
    public void shouldRejectMissingRequiredField(String field) {
        // Documents current behaviour (500). Should be 400; switch the matcher when fixed.
        client.create(BookingData.without(field)).then().statusCode(500);
    }
}
```

### Secrets/data swapped
Sample guest name replaced with generated data; credentials read from config/env.

### Needs verification
- Schemas inferred from one sample: optionality of `additionalneeds` and date format unconfirmed.
- Validation tests assert the current 500 (server error) and are tagged with `@Issue`; decide whether your suite should fail on it (strict) or document it (as here).
- Delete-of-unknown-id status not tested (behaviour undocumented).
