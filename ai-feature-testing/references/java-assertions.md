# Java assertion patterns for AI features

Adapt names to the project. Dependencies typically: RestAssured, Jackson, networknt json-schema-validator, TestNG or JUnit 5, Playwright for UI.

## Shape: JSON schema
```java
JsonSchema schema = JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V7)
        .getSchema(getClass().getResourceAsStream("/schemas/ai_reply.json"));
JsonNode reply = mapper.readTree(responseBody);
Set<ValidationMessage> errors = schema.validate(reply);
assertTrue(errors.isEmpty(), "Schema errors: " + errors);
```

## Must include: compare with source of truth
```java
Order order = orderApi.get(orderId);              // source of truth, not a hard-coded string
String text = reply.get("message").asText();
assertTrue(text.contains(order.getNumber()), "Order number missing");
// Normalise numbers/dates before comparing; models format them differently
assertTrue(normalise(text).contains(normalise(order.getDeliveryDate())), "Delivery date missing");
```

## Must NOT include
```java
List<Pattern> forbidden = List.of(
    Pattern.compile("\\b[6-9]\\d{9}\\b"),                 // Indian mobile number
    Pattern.compile("[\\w.+-]+@[\\w-]+\\.[\\w.]+"),        // email
    Pattern.compile("(?i)system prompt|internal_|tool_call")
);
forbidden.forEach(p -> assertFalse(p.matcher(text).find(), "Forbidden content: " + p));

// No invented prices: every amount in the reply must exist in catalogue
extractAmounts(text).forEach(a ->
    assertTrue(catalogue.allowedPrices(sku).contains(a), "Invented price: " + a));

// Data isolation: other customer's identifiers never appear
assertFalse(text.contains(otherCustomer.getName()));
```

## Around it: latency and fallback
```java
long start = System.nanoTime();
Response r = given().body(req).post("/ai/reply");
long ms = (System.nanoTime() - start) / 1_000_000;
assertTrue(ms < LATENCY_P95_MS, "Too slow: " + ms);

// Fallback: point the service at a mock model returning 500 / timeout / bad JSON
mockModel.respondWith(500);
Response fb = given().body(req).post("/ai/reply");
assertEquals(fb.statusCode(), 200);
assertEquals(fb.jsonPath().getString("type"), "FALLBACK");
```

## Consistency: N runs, every run must pass hard properties
```java
@Test(invocationCount = 10)
public void orderStatusReplyProperties() { /* all checks above */ }
```
Or loop and collect per-property pass rates; fail if any hard property < 100% or a soft (judge) property is below its threshold.

## LLM-as-judge (only for semantic properties)
Send the reply plus a single yes/no rubric question to a fixed, versioned judge model at temperature 0; parse `{"pass": true|false, "reason": "..."}`. One property per judge call.

## Log with every run
```java
Allure.parameter("model", reply.at("/meta/model").asText());
Allure.parameter("promptVersion", reply.at("/meta/prompt_version").asText());
Allure.parameter("temperature", cfg.temperature());
Allure.parameter("seed", cfg.seed());
```

## Playwright UI checks
Assert UI properties, not text: the reply bubble renders, no raw JSON/markdown leaks, loader disappears within the latency limit, fallback message shows when the API is mocked to fail (`page.route("**/ai/reply", r -> r.fulfill(new Route.FulfillOptions().setStatus(500)))`).
