# Input parsing

## cURL

| curl flag | Meaning | Goes to |
|---|---|---|
| `-X/--request METHOD` | method (default GET, or POST if `-d` present) | client method |
| URL | split into scheme+host (→ `baseUrl` config), path (→ client constant), query (→ `.queryParam`) | config / client |
| `-H 'Name: value'` | header | `Authorization`, `Cookie`, `X-Api-Key`, any token-looking header → config/auth setup (redacted). Others → spec or client |
| `-d/--data/--data-raw/--data-binary` | body | POJO + builder; note `Content-Type` |
| `--data-urlencode` / `-F` | form / multipart | `.formParam` / `.multiPart` |
| `-u user:pass` | basic auth | `.auth().preemptive().basic(cfg, cfg)` from config |
| `-b 'k=v'` / `--cookie` | cookies | `.cookie` from config/auth setup |
| `--compressed`, `-k`, `-s`, `-L` | transport | ignore; `-k` → mention `relaxedHTTPSValidation()` only for test envs |

Browser "Copy as cURL" includes noise headers (`sec-ch-ua*`, `user-agent`, `accept-language`, `referer`, `origin`, `priority`). Drop them unless the API is known to depend on one.

## Postman collection v2.1

```
info.name                      → @Epic
item[] (folders)               → @Feature / one test class per folder
item[].request.method/url      → endpoint
url.raw "{{baseUrl}}/x/:id"    → baseUrl config key, path param "id"
request.header[] / body.raw    → as cURL
auth (collection/folder/request; request overrides) → SpecFactory auth
variable[] / environment       → config.properties keys (values that look secret → placeholders)
event[listen=prerequest]       → setup code
event[listen=test]             → assertions
response[] (saved examples)    → schema inference + expected values
```

Common script ports:

| Postman | REST Assured / Java |
|---|---|
| `pm.response.to.have.status(200)` | `.statusCode(200)` |
| `pm.expect(pm.response.json().x).to.eql(v)` | `.body("x", equalTo(v))` |
| `pm.expect(json.items).to.have.lengthOf(n)` | `.body("items", hasSize(n))` |
| `pm.response.to.have.header("X")` | `.header("X", notNullValue())` |
| `pm.expect(pm.response.responseTime).to.be.below(500)` | `.time(lessThan(cfgMs), TimeUnit.MILLISECONDS)` |
| `pm.environment.set("token", json.token)` | return value from an auth client call, passed via SpecFactory; never a static mutable field shared across threads |
| `tv4.validate` / `pm.response.to.have.jsonSchema(s)` | schema file + `matchesJsonSchemaInClasspath` |
| `setNextRequest` chains | an explicit flow test, not test ordering |

Scripts with logic you can't map 1:1 (loops over environments, random data via `pm.variables.replaceIn('{{$randomEmail}}')`) → translate intent (Java Faker or UUID-based data) and list under "Needs verification".

## OpenAPI 3 / Swagger 2

| Spec | Tests |
|---|---|
| `paths./x.{method}` | endpoint |
| `parameters` (`in: path/query/header`), `required: true` | positive with valid value; negative with missing required query/header |
| `requestBody.content.application/json.schema` | POJO + builder; one missing-field negative per `required` property; wrong-type negatives for a few key fields |
| `enum` | valid value passes; one value outside the set fails |
| `minimum/maximum/minLength/maxLength/pattern/format` | boundary: just inside passes, just outside fails |
| `responses.{code}` | expected statuses; schema test for each code with a JSON body |
| `security` + `components.securitySchemes` | auth setup; 401 negatives for protected ops; skip auth negatives for ops with `security: []` |
| `deprecated: true` | still test, tag `@Story("deprecated")`, mention in output |
| `examples` / `example` | use as test data (after swapping any personal data) |

Swagger 2: `definitions` instead of `components.schemas`, `parameters[in: body]` instead of `requestBody`, `securityDefinitions` instead of `securitySchemes`.

## OpenAPI 3.0 schema → JSON Schema draft-04 (REST Assured validator)

- Add `"$schema": "http://json-schema.org/draft-04/schema#"`. REST Assured's validator is draft-04 only.
- `exclusiveMinimum: true` (OpenAPI 3.0) maps directly (draft-04 also uses booleans). OpenAPI 3.1 numeric `exclusiveMinimum: 5` → `"minimum": 5, "exclusiveMinimum": true`.
- `const: X` → `"enum": [X]`.
- `nullable: true` + `type: X` → `"type": ["X", "null"]` (enum: add `null` to the enum too).
- `$ref: '#/components/schemas/Foo'` → move referenced schemas under `"definitions"` and rewrite to `"#/definitions/Foo"` (or inline if used once).
- Drop OpenAPI-only keywords: `example`, `xml`, `discriminator` (keep `oneOf`), `readOnly`/`writeOnly` (but don't require writeOnly fields in responses, and don't send readOnly fields in requests).
- `format`: draft-04 validates `date-time`, `email`, `uri`, `ipv4`, `ipv6`, `hostname`. `uuid`, `date` and custom formats are ignored with a warning, so add a `pattern` when it matters (uuid: `^[0-9a-fA-F-]{36}$`, date: `^\\d{4}-\\d{2}-\\d{2}$`).
- Keep `additionalProperties` only if the spec sets it.
- OpenAPI 3.1 uses JSON Schema 2020-12: downgrade (`const`, numeric exclusives, `$defs` → `definitions`, `prefixItems` → `items` array) for draft-04, or note it.

## HAR

`log.entries[].request` → like cURL (method, url, headers, postData.text). `log.entries[].response.content.text` → sample for schema inference and assertions. Filter to the API host and XHR/fetch entries; ignore static assets, analytics and third-party hosts.
