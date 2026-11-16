# Dialect notes

| Need | PostgreSQL / Redshift | MySQL | SQL Server | BigQuery | Snowflake |
|---|---|---|---|---|---|
| Limit rows | `LIMIT 20` | `LIMIT 20` | `SELECT TOP 20` | `LIMIT 20` | `LIMIT 20` |
| Today | `CURRENT_DATE` | `CURDATE()` | `CAST(GETDATE() AS date)` | `CURRENT_DATE()` | `CURRENT_DATE` |
| Days ago | `CURRENT_DATE - INTERVAL '3 days'` (Redshift: `DATEADD(day,-3,CURRENT_DATE)`) | `CURDATE() - INTERVAL 3 DAY` | `DATEADD(day,-3,GETDATE())` | `DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY)` | `DATEADD(day,-3,CURRENT_DATE)` |
| Case-insensitive match | `ILIKE '%x%'` | `LIKE` (default collation) | `LIKE` (default collation) | `LOWER(col) LIKE '%x%'` | `ILIKE '%x%'` |
| JSON field | `col->>'key'` (Redshift: `JSON_EXTRACT_PATH_TEXT(col,'key')`) | `col->>'$.key'` | `JSON_VALUE(col,'$.key')` | `JSON_VALUE(col,'$.key')` | `col:key::string` |
| Random sample | `ORDER BY RANDOM()` | `ORDER BY RAND()` | `ORDER BY NEWID()` | `ORDER BY RAND()` | `SAMPLE (20 ROWS)` |

Redshift is PostgreSQL-like but lacks some features (no `ILIKE` on some types, JSON via functions, limited window/regex behaviour); prefer simple constructs.
