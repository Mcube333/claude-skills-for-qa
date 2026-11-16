---
name: api-contract-diff
description: Compare two versions of an API contract and report what changed and what will break clients - from two OpenAPI/Swagger specs, two JSON response samples, two HAR captures, or old vs new Postman examples. Classifies each change as breaking, risky or safe (removed or renamed fields, type changes, required/optional flips, enum values added or removed, nullability, format, status codes, endpoints added or removed), points out likely renames, and turns the result into test cases and a client-impact list for web, iOS and Android. Use this whenever the user shares two API responses or specs and asks "what changed", "is this breaking", "compare old and new response", "contract test", "backend changed the API", or a client broke after a backend release - even if they don't say "contract".
---

# API Contract Diff

Mobile apps in users' hands cannot be updated instantly, so a backend change that renames a field or
changes a type can break old app versions for weeks. Comparing contracts before release catches this
when it is still cheap to fix.

## Inputs
- Two OpenAPI/Swagger documents (YAML or JSON), or
- Two JSON responses for the same endpoint (old vs new), or
- Two HAR files (the script extracts JSON responses per endpoint), or
- One spec and one real response (does production match the spec?)

## Workflow

1. **Normalise both sides** to a map of field paths -> type (e.g. `data.items[].price: number`).
   For JSON samples and HAR files run `scripts/json_shape_diff.py`; for OpenAPI compare schemas,
   required lists, enums, nullable, formats, status codes and endpoints directly.
2. **Classify every difference** using `references/change-rules.md`:
   - **Breaking:** removed field/endpoint, type change, optional -> required in a request, enum value
     removed from a response, field made nullable where clients expect a value, status code change, auth change.
   - **Risky:** new enum value in a response (old clients may not handle it), format change (date string
     format, number precision), array that can now be empty, default value change, field order if clients parse positionally.
   - **Safe:** new optional field in a response, new endpoint, new optional request parameter, docs-only changes.
3. **Detect likely renames:** a removed field and an added field with the same type and similar name or
   value (e.g. `price_total` -> `totalPrice`) are reported as "possible rename", which is breaking for
   old clients.
4. **Explain client impact** per platform where known (old app versions, web, partners), and whether a
   compatibility shim (keep old field, add new) is needed.
5. **Turn it into tests:** for each breaking or risky change, a contract test assertion (schema check) and
   an end-to-end check on the screen that uses the field.

## Output

```
## Contract diff: <endpoint or spec> (<old version> -> <new version>)

Verdict: <Breaking / Risky / Safe> - <one line>

| Path | Change | Old | New | Class | Client impact |
(breaking first)

Possible renames:
- old.path -> new.path (same type, similar name/values)

Tests to add:
1. Contract: <assertion>
2. E2E: <screen + check>

Recommendation: <ship / ship with shim / block>, <who to tell>
```
