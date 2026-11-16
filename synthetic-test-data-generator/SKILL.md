---
name: synthetic-test-data-generator
description: Generate realistic but completely fake test data - users, addresses, phone numbers, emails, orders, products, payments, subscriptions or any custom entity - for any domain and country, as CSV, JSON, SQL seed (for test environments only) or code fixtures (Java, Python, JS). Covers happy-path, boundary and negative values, keeps records consistent with each other (order totals match lines, dates in order), uses reserved/test values so nothing can reach a real person (example.com emails, reserved phone ranges, gateway test cards), and is reproducible with a seed. Use this whenever the user needs test data, fixtures, seed data, sample payloads, a CSV of users, data for a data-driven test, or boundary/negative inputs for a form or API - even if they don't say "synthetic".
---

# Synthetic Test Data Generator

Test data needs to look real enough to exercise the code, but must never be real: no actual people,
deliverable emails, live phone numbers or working cards. It also has to be internally consistent, or
tests fail for the wrong reason.

## Workflow

1. **Clarify the shape:** entities and fields (or a sample record/schema the user shares), count,
   country/locale (affects phone, postcode, currency, names, address format), output format, and
   whether related entities are needed (users -> orders -> payments).
2. **Choose the mix:** by default ~70% valid typical records, ~20% boundary values, ~10% negative/invalid
   (only if the user wants negative cases; label them in a `case_type` column). See
   `references/value-catalogue.md` for boundary and negative values per field type.
3. **Keep it safe:** emails on `example.com` / `example.org`; phone numbers from reserved or obviously
   fake ranges (or all-zero subscriber numbers); payment cards only from the gateway's published test
   numbers; IDs prefixed (e.g. `TEST-`); never real addresses of real buildings when avoidable.
4. **Keep it consistent:** totals equal the sum of lines, created < updated < delivered dates, statuses
   valid for their dates, foreign keys point to generated parents, unique fields unique.
5. **Make it reproducible:** use `scripts/generate.py` with a fixed `--seed` for larger sets so the same
   data can be regenerated in CI. For small sets (< 30 rows) write the data directly.

## Using the script

`scripts/generate.py` uses only the Python standard library:

```
python scripts/generate.py --entity users --count 50 --locale IN --seed 42 --format csv > users.csv
python scripts/generate.py --entity orders --count 100 --seed 7 --format json > orders.json
python scripts/generate.py --entity users --count 20 --with-edge-cases --format csv
```

Entities: `users`, `orders` (with line items and consistent totals), `products`. For other entities,
extend the script or write the data directly following the same safety rules.

## Output

The data in the requested format, then 2-3 lines: how many records of each case type, the seed used,
and any field you had to assume.
