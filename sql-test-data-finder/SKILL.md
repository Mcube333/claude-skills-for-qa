---
name: sql-test-data-finder
description: Write safe, read-only SQL to find test accounts and records that match a QA scenario described in plain English ("a user with an overdue renewal and an active cart", "orders paid but not delivered for over 3 days", "products out of stock in one city only"), and to run data-integrity checks (orphans, duplicates, totals that don't add up, invalid states). Works with any SQL dialect (PostgreSQL, MySQL, Redshift, BigQuery, Snowflake, SQL Server) and any schema the user shares as DDL, table/column lists, sample rows or ER notes; asks for the schema rather than inventing it. Use this whenever the user needs test data from a database, asks for a query to find users/orders/products in some state, wants to verify data after a test or migration, or pastes table definitions with a QA question - even if they don't say "SQL".
---

# SQL Test Data Finder

Testers lose hours hunting for the right account. A good query finds it in seconds - but a wrong
one can lock tables, leak personal data or quietly return the wrong users. This skill writes queries
that are correct for the schema, cheap to run and safe.

## Ground rules

- **Read-only.** SELECT (and CTEs) only. Never write INSERT, UPDATE, DELETE, MERGE, DDL or anything that
  changes data. If the user needs data created or changed, describe it as a request for the owning
  team or a seed script for a test environment, and say clearly that it must not run on production.
- **No invented schema.** Use only tables and columns the user has shown. If something needed is
  missing, ask for it or write the query with clearly marked placeholders like `<orders_table>` and
  list what to fill in.
- **Cheap by default.** Filter early, select only needed columns, add `LIMIT` (or `TOP`) for lookups,
  prefer indexed keys and date-range filters on large tables. Warn when a query will scan a big table.
- **Privacy.** Select IDs, statuses and dates. Avoid selecting names, phones, emails, addresses or
  payment details unless the user explicitly needs a contact field to log in with a test account, and
  then only from a test environment. Mask in outputs where possible.
- **Dialect-aware.** Ask which database if unclear; date functions, string matching, LIMIT/TOP and
  JSON handling differ. See `references/dialect-notes.md`.

## Workflow

1. **Restate the scenario** as precise conditions (e.g. "renewal due date < today AND status not
   'paid' AND cart has >= 1 active item"). Point out ambiguities ("active" means what status values?)
   and pick a sensible default if the user wants speed.
2. **Map conditions to tables and joins** using the schema. Watch for: one-to-many joins that duplicate
   rows (use EXISTS or aggregate first), soft-deleted rows, timezone of timestamps, test vs real users.
3. **Write the query** with a short comment per block. Use CTEs for readability.
4. **Add a verification query** when the scenario is complex: e.g. for each returned user, show the
   fields that prove they match, so the tester can trust the result before using the account.
5. **Explain how to use the result** in the test (which ID to log in with, what state it should show).

## Data-integrity checks

When asked to validate data (after a test run, migration or bug), use the patterns in
`references/integrity-patterns.md`: orphans, duplicates, totals mismatch, invalid state combinations,
nulls in required fields, out-of-range values, referential gaps across services.

## Output

```
Scenario: <precise conditions>
Assumptions: <status values, timezone, dialect>

-- query
<SQL>

-- verify (optional)
<SQL>

How to use: <one or two lines>
Fill in before running: <placeholders, if any>
```
