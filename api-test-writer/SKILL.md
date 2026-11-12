---
name: api-test-writer
description: Generate REST Assured (Java) API tests with JSON schema validation from a cURL command, a Postman collection, an OpenAPI/Swagger spec, or a HAR/request capture. Produces service-layer client classes, positive, negative and contract tests, schema files, TestNG + Allure reporting, and an endpoint coverage matrix. Use this whenever the user pastes a curl, shares a Postman collection/export, an OpenAPI or Swagger yaml/json, or asks to "write API tests", "automate this endpoint", "add contract/schema tests", "convert Postman tests to Java", or "REST Assured tests for this", even if they don't name REST Assured but clearly want Java API automation.
---

# API Test Writer (REST Assured)

Turn an API description into a test suite an SDET would be comfortable owning: a thin service layer, tests that check behaviour and contract, negatives that matter, no hard-coded secrets, and a coverage matrix that shows what is and isn't tested.

## 1. Identify the input and parse it

Read `references/input-parsing.md` for the detailed mapping. Summary:

- **cURL**: method, URL (split base URL vs path vs query), headers, body, auth. One endpoint, usually with no response sample unless the user pastes one.
- **Postman collection (v2.1 JSON)**: every item → endpoint; `{{variables}}` → config keys; collection/folder auth → shared auth; pre-request scripts that set tokens → setup methods; `pm.test` scripts → assertions to port; saved example responses → schema/assertion source.
- **OpenAPI 3 / Swagger 2**: paths × methods → endpoints; `components.schemas` → JSON schema files and POJOs; `required`, `enum`, `minLength`, `format`, etc. → negative and boundary cases; `responses` → expected status codes; `securitySchemes` → auth setup.
- **HAR / captured requests**: treat each entry like a cURL with a real response sample.

Build an **endpoint inventory** first (method, path, auth, request schema, response codes, sample available yes/no). If there are more than ~10 endpoints, generate the framework plus tests for the inventory in priority order (critical flows first) and say what's left, rather than producing shallow tests for everything.

## 2. Secrets and data hygiene (always)

- Never copy tokens, cookies, API keys, passwords, or session ids from the input into code. Replace with config/env lookups (`ConfigReader.get("auth.token")` or an auth-setup call) and say you did.
- Replace real personal data in bodies/samples (names, phones, emails, addresses) with generated test data.
- For portfolio/public work, also replace internal hostnames, company names, and internal path prefixes with neutral ones, and mention the swap in one line.

## 3. Design the tests

For each endpoint, choose from these categories. Not every endpoint needs all of them; pick what the spec or sample actually supports, and don't invent business rules.

| Category | Typical tests |
|---|---|
| Positive | Valid request → expected status, content-type, schema, key field values echo the request |
| Contract | Response matches JSON schema (every documented status code that has a body, not just 2xx) |
| Auth | No credentials → 401; invalid/expired → 401/403; only if the endpoint is protected |
| Validation | Each **required** field missing → 400/422; wrong type; enum value outside the set; min/max boundaries (just inside passes, just outside fails) |
| Not found | Unknown id → 404 |
| Flow | Create → read → update → read → delete → read-404, with cleanup in `finally`/`@AfterMethod` |
| Idempotency/headers | Only when the spec documents them (ETag, Idempotency-Key, pagination links) |

If the expected error status isn't documented, write the test asserting `4xx` (`anyOf(400, 422)`) and list it under "Needs verification" rather than guessing one code.

Response-time assertions are optional and only as a loose guard read from config (`maxResponseMs`), never as a performance test.

## 4. Code structure

Follow `references/framework-scaffold.md`. Key rules:

- **SpecFactory** builds `RequestSpecification`/`ResponseSpecification` instances (base URI, content type, auth, Allure filter, logging on failure). Do **not** mutate `RestAssured.baseURI` or other static globals in tests; static config breaks parallel runs.
- **Service/client classes** per resource (`BookingClient.create(payload)`, `.get(id)`) return `Response` (or `ValidatableResponse`). Tests never build raw requests inline except for deliberately malformed negatives.
- **Payloads**: POJOs + builders (Jackson) for valid requests; `Map`/raw JSON string for invalid ones (missing field, wrong type), since POJOs can't express those.
- **Schemas** in `src/test/resources/schemas/<resource>/<name>.json`, validated with `matchesJsonSchemaInClasspath`.
- **State-mutating tests on shared data** (no create endpoint available): capture the original state in setup and restore it after each test; if it can't be read, say so and note that the tests can't run in parallel.
- **Tests**: TestNG, one behaviour per method, `@Epic/@Feature/@Story/@Severity`, `@TmsLink` if case IDs exist. Data-driven negatives via `@DataProvider` with a readable case label as the first column.
- Assert with Hamcrest on the `ValidatableResponse` (`statusCode`, `body("path", equalTo(...))`, `header`). Prefer specific values the request determined over "not null".
- Tests are independent: create their own data, clean it up, never depend on order or on pre-existing ids in an environment.

## 5. JSON schemas

- **From OpenAPI**: convert the component schema faithfully (`required`, `enum`, `format`, `nullable` → `"type": ["x", "null"]`, `$ref` inlined or resolved via `definitions`). Use **draft-04** (`"$schema": "http://json-schema.org/draft-04/schema#"`): REST Assured's `json-schema-validator` module only supports draft-04. So no `const` (use a one-value `enum`), `exclusiveMinimum`/`exclusiveMaximum` are booleans next to `minimum`/`maximum`, no `if/then/else`, and `format` values other than `date-time`/`email`/`uri`/`ipv4`/`ipv6`/`hostname` (e.g. `uuid`, `date`) are ignored: add a `pattern` where the format matters. If the user needs newer drafts, suggest the networknt `json-schema-validator` library instead.
- **From a single sample response**: infer types; mark fields `required` only if they look like core identifiers/fields, and **don't** set `additionalProperties: false`. Put `"description": "Inferred from one sample - verify against the API contract"` at the top. One sample can't tell you which fields are optional or nullable, so flag it.
- Never generate a schema so loose it can't fail (e.g. only `"type": "object"`).

## Output format

1. **Endpoint inventory / coverage matrix**: `Endpoint | Positive | Contract | Auth | Validation | Not found | Flow`, with ✓, ✗ (not applicable), or `gap`.
2. **Files**: full compilable files with imports under path headings: config, SpecFactory/BaseApiTest (only if no framework exists or the user asks), clients, POJOs/builders, schemas, tests. If more than ~3 files or the user wants to download, also write them to disk as a project folder.
3. **Secrets/data swapped**: one or two lines.
4. **Needs verification**: undocumented error codes, inferred schemas, assumed business rules, ported Postman scripts that had logic you couldn't translate.

Keep prose short; the code is the deliverable.

## Reference files

- `references/input-parsing.md`: cURL flag mapping, Postman v2.1 structure and script porting, OpenAPI → tests/schemas mapping, OpenAPI 3.0 → JSON Schema conversion rules.
- `references/framework-scaffold.md`: pom.xml, config, SpecFactory, BaseApiTest, client class, POJO/builder, schema validation, Allure filter, data providers.
- `references/example-restful-booker.md`: full worked example on the public restful-booker API, including its quirks.
