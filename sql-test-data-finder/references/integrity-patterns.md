# Integrity check patterns (placeholders in <>)

-- Orphans: child rows whose parent is missing
SELECT c.id FROM <child> c LEFT JOIN <parent> p ON p.id = c.<parent_id> WHERE p.id IS NULL;

-- Duplicates on a business key
SELECT <key_cols>, COUNT(*) FROM <table> GROUP BY <key_cols> HAVING COUNT(*) > 1;

-- Header total vs sum of lines
SELECT h.id, h.total, SUM(l.amount) AS lines_total
FROM <header> h JOIN <lines> l ON l.<header_id> = h.id
GROUP BY h.id, h.total
HAVING ABS(h.total - SUM(l.amount)) > 0.01;

-- Invalid state combinations (example: paid but no payment record)
SELECT o.id FROM <orders> o
WHERE o.status = '<paid_status>'
  AND NOT EXISTS (SELECT 1 FROM <payments> p WHERE p.<order_id> = o.id AND p.status = '<captured_status>');

-- Required fields missing
SELECT id FROM <table> WHERE <required_col> IS NULL OR TRIM(<required_col>) = '';

-- Out of range
SELECT id, <col> FROM <table> WHERE <col> < <min> OR <col> > <max>;

-- Same entity, different values across two tables/services
SELECT a.id, a.<col> AS a_val, b.<col> AS b_val
FROM <table_a> a JOIN <table_b> b ON b.<ref> = a.id
WHERE a.<col> <> b.<col>;
