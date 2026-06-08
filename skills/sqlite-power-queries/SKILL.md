---
name: sqlite-power-queries
description: >
  Advanced SQLite patterns: window functions, CTEs, recursive queries, JSON
  columns, FTS5 full-text search, and Python sqlite3 best practices. TRIGGER:
  user says "sqlite", "window function", "CTE", "recursive SQL", "sqlite json",
  "full-text search", "sqlite3 python", "rank over partition", or
  "sqlite advanced".
---

# SQLite Power Queries

> **Purpose**: Go beyond basic SELECT/INSERT — leverage SQLite's advanced
> features for analytics, hierarchical data, full-text search, and JSON
> storage. All patterns work with Python's built-in `sqlite3` module and
> Django's SQLite backend.

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Setup & Python Basics](#setup--python-basics)
3. [CTEs — Common Table Expressions](#ctes--common-table-expressions)
4. [Recursive CTEs](#recursive-ctes)
5. [Window Functions](#window-functions)
6. [JSON Columns](#json-columns)
7. [Full-Text Search (FTS5)](#full-text-search-fts5)
8. [Aggregation Patterns](#aggregation-patterns)
9. [Performance — Indexes & EXPLAIN](#performance--indexes--explain)
10. [Python sqlite3 Best Practices](#python-sqlite3-best-practices)
11. [Django Raw SQL with SQLite](#django-raw-sql-with-sqlite)
12. [Useful Pragmas](#useful-pragmas)
13. [Lessons Learned](#lessons-learned)

---

## Quick Reference

```sql
-- CTE
WITH monthly AS (
    SELECT strftime('%Y-%m', date) AS month, SUM(amount) AS total
    FROM transactions GROUP BY month
)
SELECT * FROM monthly ORDER BY month;

-- Window function: rank within group
SELECT name, dept, salary,
       RANK() OVER (PARTITION BY dept ORDER BY salary DESC) AS rank_in_dept
FROM employees;

-- JSON column access
SELECT json_extract(metadata, '$.tags[0]') FROM items;

-- FTS5 full-text search
SELECT * FROM docs_fts WHERE docs_fts MATCH 'silicon AND package';
```

---

## Setup & Python Basics

```python
import sqlite3
from contextlib import contextmanager

# Connect (creates file if missing)
conn = sqlite3.connect("app.db")

# Row factory — access columns by name
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Enable WAL mode (better concurrent reads)
conn.execute("PRAGMA journal_mode=WAL")

# Context manager for transactions
@contextmanager
def get_db(path="app.db"):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

# Usage
with get_db() as db:
    rows = db.execute("SELECT * FROM items WHERE active = 1").fetchall()
    for row in rows:
        print(row["name"], row["created_at"])   # column name access
```

---

## CTEs — Common Table Expressions

CTEs make complex queries readable by naming intermediate results.

```sql
-- Basic CTE: monthly revenue summary
WITH monthly_revenue AS (
    SELECT
        strftime('%Y-%m', order_date) AS month,
        SUM(total_amount)             AS revenue,
        COUNT(*)                      AS order_count
    FROM orders
    WHERE status = 'completed'
    GROUP BY strftime('%Y-%m', order_date)
),
running_total AS (
    SELECT
        month,
        revenue,
        order_count,
        SUM(revenue) OVER (ORDER BY month) AS cumulative_revenue
    FROM monthly_revenue
)
SELECT * FROM running_total ORDER BY month;
```

```sql
-- Multiple CTEs (chained)
WITH active_users AS (
    SELECT id, name FROM users WHERE active = 1
),
user_order_counts AS (
    SELECT user_id, COUNT(*) AS num_orders FROM orders GROUP BY user_id
),
power_users AS (
    SELECT u.id, u.name, uoc.num_orders
    FROM active_users u
    JOIN user_order_counts uoc ON u.id = uoc.user_id
    WHERE uoc.num_orders >= 10
)
SELECT * FROM power_users ORDER BY num_orders DESC;
```

```python
# Python — parametrized CTE
with get_db() as db:
    rows = db.execute("""
        WITH dept_stats AS (
            SELECT dept, AVG(salary) AS avg_sal, COUNT(*) AS headcount
            FROM employees
            GROUP BY dept
        )
        SELECT e.name, e.salary, d.avg_sal,
               ROUND((e.salary - d.avg_sal) / d.avg_sal * 100, 1) AS pct_above_avg
        FROM employees e
        JOIN dept_stats d ON e.dept = d.dept
        WHERE e.dept = ?
        ORDER BY e.salary DESC
    """, ("Engineering",)).fetchall()
```

---

## Recursive CTEs

Recursive CTEs traverse hierarchical data (org charts, category trees, bill of materials).

```sql
-- Org chart: find all reports under a manager
WITH RECURSIVE reports AS (
    -- Base case: the manager themselves
    SELECT id, name, manager_id, 0 AS depth
    FROM employees
    WHERE id = 42                       -- starting manager ID

    UNION ALL

    -- Recursive step: add each direct report
    SELECT e.id, e.name, e.manager_id, r.depth + 1
    FROM employees e
    JOIN reports r ON e.manager_id = r.id
)
SELECT depth, name FROM reports ORDER BY depth, name;
```

```sql
-- Category tree: find all subcategories (unlimited depth)
WITH RECURSIVE subcategories AS (
    SELECT id, name, parent_id, name AS path
    FROM categories
    WHERE parent_id IS NULL              -- root categories

    UNION ALL

    SELECT c.id, c.name, c.parent_id,
           sc.path || ' > ' || c.name   -- build breadcrumb path
    FROM categories c
    JOIN subcategories sc ON c.parent_id = sc.id
)
SELECT path, name FROM subcategories ORDER BY path;
```

```sql
-- Number sequence (1 to 100) — useful for date ranges
WITH RECURSIVE nums(n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1 FROM nums WHERE n < 100
)
SELECT n FROM nums;

-- Date range
WITH RECURSIVE dates(d) AS (
    SELECT date('2025-01-01')
    UNION ALL
    SELECT date(d, '+1 day') FROM dates WHERE d < date('2025-12-31')
)
SELECT d FROM dates;
```

---

## Window Functions

Window functions compute values across a "window" of rows without collapsing them.

```sql
-- RANK, DENSE_RANK, ROW_NUMBER
SELECT
    name,
    dept,
    salary,
    RANK()       OVER (PARTITION BY dept ORDER BY salary DESC) AS rank,
    DENSE_RANK() OVER (PARTITION BY dept ORDER BY salary DESC) AS dense_rank,
    ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) AS row_num
FROM employees;
```

```sql
-- Running total and moving average
SELECT
    date,
    amount,
    SUM(amount)  OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
        AS running_total,
    AVG(amount)  OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
        AS rolling_7day_avg
FROM daily_sales;
```

```sql
-- Compare to previous/next row (LAG/LEAD)
SELECT
    date,
    revenue,
    LAG(revenue, 1, 0) OVER (ORDER BY date)   AS prev_day,
    LEAD(revenue, 1, 0) OVER (ORDER BY date)  AS next_day,
    revenue - LAG(revenue, 1, 0) OVER (ORDER BY date) AS day_over_day_change
FROM daily_revenue;
```

```sql
-- NTILE: divide into N equal buckets (percentiles)
SELECT
    name,
    salary,
    NTILE(4) OVER (ORDER BY salary) AS salary_quartile  -- 1=bottom, 4=top
FROM employees;
```

```sql
-- FIRST_VALUE / LAST_VALUE
SELECT
    dept,
    name,
    salary,
    FIRST_VALUE(name)  OVER (PARTITION BY dept ORDER BY salary DESC) AS top_earner,
    LAST_VALUE(salary) OVER (PARTITION BY dept ORDER BY salary
                             ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
        AS min_salary_in_dept
FROM employees;
```

---

## JSON Columns

SQLite has built-in JSON functions since version 3.38 (2022).

```sql
-- Store JSON in a TEXT column
CREATE TABLE events (
    id       INTEGER PRIMARY KEY,
    type     TEXT,
    payload  TEXT    -- JSON stored as text
);

INSERT INTO events (type, payload) VALUES
    ('user_login',  '{"user_id": 42, "ip": "10.0.0.1", "tags": ["admin", "beta"]}'),
    ('purchase',    '{"user_id": 7,  "amount": 99.99, "items": [{"sku": "A1"}, {"sku": "B2"}]}');

-- Extract a field
SELECT json_extract(payload, '$.user_id')         AS user_id FROM events;
SELECT json_extract(payload, '$.tags[0]')         AS first_tag FROM events;
SELECT json_extract(payload, '$.items[0].sku')    AS first_sku FROM events;

-- Filter on JSON field
SELECT * FROM events
WHERE json_extract(payload, '$.amount') > 50;

-- Check array contains value
SELECT * FROM events
WHERE EXISTS (
    SELECT 1 FROM json_each(json_extract(payload, '$.tags'))
    WHERE value = 'admin'
);

-- Expand JSON array into rows
SELECT e.id, tag.value AS tag
FROM events e, json_each(json_extract(e.payload, '$.tags')) AS tag
WHERE e.type = 'user_login';

-- Build JSON from query
SELECT json_object('id', id, 'type', type) FROM events;
SELECT json_group_array(json_object('id', id, 'type', type)) FROM events;
```

```python
# Python — store and retrieve JSON
import sqlite3, json

conn = sqlite3.connect("app.db")
conn.execute("CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)")

# Store
data = {"threshold": 0.95, "models": ["gemma3", "phi4"], "active": True}
conn.execute("INSERT OR REPLACE INTO config VALUES (?, ?)",
             ("ai_settings", json.dumps(data)))
conn.commit()

# Retrieve
row = conn.execute("SELECT value FROM config WHERE key = ?", ("ai_settings",)).fetchone()
settings = json.loads(row[0])
print(settings["models"])   # ["gemma3", "phi4"]
```

---

## Full-Text Search (FTS5)

FTS5 enables fast keyword search over large text columns.

```sql
-- Create FTS5 virtual table
CREATE VIRTUAL TABLE docs_fts USING fts5(
    title,
    body,
    content='documents',     -- shadow table to keep data in sync
    content_rowid='id'
);

-- Populate from existing table
INSERT INTO docs_fts(rowid, title, body)
    SELECT id, title, body FROM documents;

-- Simple search
SELECT * FROM docs_fts WHERE docs_fts MATCH 'silicon';

-- AND / OR / NOT
SELECT * FROM docs_fts WHERE docs_fts MATCH 'silicon AND package';
SELECT * FROM docs_fts WHERE docs_fts MATCH 'package OR substrate';
SELECT * FROM docs_fts WHERE docs_fts MATCH 'silicon NOT copper';

-- Phrase search
SELECT * FROM docs_fts WHERE docs_fts MATCH '"package substrate"';

-- Prefix match
SELECT * FROM docs_fts WHERE docs_fts MATCH 'semi*';

-- Field-specific search
SELECT * FROM docs_fts WHERE docs_fts MATCH 'title:LOAKS body:crossbar';

-- Ranked results (BM25 relevance scoring)
SELECT title, rank FROM docs_fts
WHERE docs_fts MATCH 'silicon package'
ORDER BY rank;   -- rank is negative; smaller = more relevant

-- Highlight matching terms
SELECT highlight(docs_fts, 1, '<b>', '</b>') AS highlighted_body
FROM docs_fts WHERE docs_fts MATCH 'silicon';

-- Snippet (context window around match)
SELECT snippet(docs_fts, 1, '[', ']', '...', 10) AS snippet
FROM docs_fts WHERE docs_fts MATCH 'silicon';
```

```python
# Python FTS5 integration
with get_db() as db:
    db.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS search_idx USING fts5(
            title, content, tokenize='porter ascii'
        )
    """)

    # Index documents
    docs = db.execute("SELECT id, title, body FROM documents").fetchall()
    db.executemany(
        "INSERT INTO search_idx(rowid, title, content) VALUES (?, ?, ?)",
        [(row["id"], row["title"], row["body"]) for row in docs]
    )

    # Search
    results = db.execute("""
        SELECT rowid, title, snippet(search_idx, 1, '[', ']', '...', 15) AS excerpt
        FROM search_idx
        WHERE search_idx MATCH ?
        ORDER BY rank
        LIMIT 10
    """, ("silicon package",)).fetchall()

    for r in results:
        print(r["title"], "|", r["excerpt"])
```

---

## Aggregation Patterns

```sql
-- Conditional aggregation (pivot-like)
SELECT
    dept,
    COUNT(*) AS total,
    SUM(CASE WHEN gender = 'M' THEN 1 ELSE 0 END) AS male_count,
    SUM(CASE WHEN gender = 'F' THEN 1 ELSE 0 END) AS female_count,
    AVG(CASE WHEN level = 'Senior' THEN salary END) AS avg_senior_salary
FROM employees
GROUP BY dept;

-- GROUP_CONCAT — join values into a string
SELECT dept, GROUP_CONCAT(name, ', ') AS members
FROM employees
GROUP BY dept;

-- Median (no built-in, use window trick)
SELECT dept,
       AVG(salary) AS avg_salary,
       (SELECT salary FROM (
           SELECT salary, ROW_NUMBER() OVER (ORDER BY salary) AS rn,
                  COUNT(*) OVER () AS total
           FROM employees e2 WHERE e2.dept = e1.dept
       ) WHERE rn = (total + 1) / 2) AS median_salary
FROM employees e1
GROUP BY dept;

-- Top-N per group (using window function)
SELECT dept, name, salary FROM (
    SELECT dept, name, salary,
           ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) AS rn
    FROM employees
)
WHERE rn <= 3;   -- top 3 earners per department
```

---

## Performance — Indexes & EXPLAIN

```sql
-- Create indexes
CREATE INDEX idx_employees_dept ON employees(dept);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_events_user ON events(json_extract(payload, '$.user_id'));  -- expression index

-- Composite index (left-most prefix rule)
CREATE INDEX idx_orders_user_date ON orders(user_id, order_date);
-- Useful for: WHERE user_id = ? (yes), WHERE user_id = ? AND order_date > ? (yes)
-- NOT useful for: WHERE order_date > ? alone (no)

-- Check query plan
EXPLAIN QUERY PLAN
SELECT * FROM employees WHERE dept = 'Engineering' ORDER BY salary DESC;
-- Look for: "SEARCH employees USING INDEX" (good) vs "SCAN employees" (bad)

-- Analyze (update statistics for query planner)
ANALYZE;
```

---

## Python sqlite3 Best Practices

```python
import sqlite3
from typing import Any

# Always use parameterized queries — NEVER string formatting
# WRONG (SQL injection risk):
# cursor.execute(f"SELECT * FROM users WHERE name = '{name}'")

# CORRECT:
cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
cursor.execute("SELECT * FROM users WHERE id IN (?,?,?)", (1, 2, 3))

# Named parameters (clearer for many params)
cursor.execute(
    "INSERT INTO events (type, user_id, ts) VALUES (:type, :user, :ts)",
    {"type": "login", "user": 42, "ts": "2025-05-01"}
)

# Batch insert (much faster than individual INSERTs)
data = [("Alice", 30), ("Bob", 25), ("Carol", 35)]
conn.executemany("INSERT INTO users (name, age) VALUES (?, ?)", data)

# Read as dicts
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT * FROM users").fetchall()
print(dict(rows[0]))   # {"id": 1, "name": "Alice", "age": 30}

# Upsert (INSERT OR REPLACE / ON CONFLICT)
conn.execute("""
    INSERT INTO config (key, value) VALUES (?, ?)
    ON CONFLICT(key) DO UPDATE SET value = excluded.value
""", ("theme", "dark"))

# Transaction batching (massive speed improvement for bulk writes)
conn.execute("BEGIN TRANSACTION")
for item in large_list:
    conn.execute("INSERT INTO items VALUES (?)", (item,))
conn.execute("COMMIT")
# Or use: conn.executemany() which handles this automatically
```

---

## Django Raw SQL with SQLite

```python
from django.db import connection

# Raw SQL with Django's connection
def get_top_earners_per_dept(n=3):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT dept, name, salary FROM (
                SELECT dept, name, salary,
                       ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) AS rn
                FROM myapp_employee
            )
            WHERE rn <= %s
        """, [n])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

# FTS5 with Django
def full_text_search(query: str):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT d.id, d.title, snippet(docs_fts, 1, '<b>', '</b>', '...', 20) AS excerpt
            FROM docs_fts
            JOIN myapp_document d ON d.id = docs_fts.rowid
            WHERE docs_fts MATCH %s
            ORDER BY rank
            LIMIT 20
        """, [query])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
```

---

## Useful Pragmas

```sql
-- Performance
PRAGMA journal_mode=WAL;          -- better concurrent read performance
PRAGMA synchronous=NORMAL;        -- safer than OFF, faster than FULL
PRAGMA cache_size=-64000;         -- 64MB page cache (negative = KB)
PRAGMA temp_store=MEMORY;         -- temp tables in RAM

-- Data integrity
PRAGMA foreign_keys=ON;           -- enforce FK constraints (OFF by default!)
PRAGMA integrity_check;           -- full DB integrity check
PRAGMA quick_check;               -- faster, less thorough

-- Info
PRAGMA table_info(employees);     -- column names and types
PRAGMA index_list(employees);     -- indexes on a table
PRAGMA database_list;             -- attached databases
PRAGMA user_version;              -- app-managed schema version number

-- Schema version tracking (Django-style manual migrations)
PRAGMA user_version = 5;          -- set schema version
```

```python
# Enable pragmas in Python on every connection
def configure_db(conn: sqlite3.Connection):
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=-32000")   # 32MB
```

---

## Lessons Learned

- **`PRAGMA foreign_keys=ON` must be set every connection** — SQLite disables
  FK enforcement by default. Set it in your connection factory.
- **WAL mode is almost always better** for web apps: readers never block
  writers and vice versa.
- **Window functions require SQLite 3.25+** (2018). All modern Python
  distributions include this.
- **FTS5 is not available in older SQLite** — check with `SELECT sqlite_version()`.
  Version 3.20+ (2017) has FTS5 with all features.
- **JSON functions require SQLite 3.38+** (2022) for `json_each()` improvements.
  For older versions, use `json_extract()` which has been available since 3.9.
- **`executemany()` vs loop**: Use `executemany()` for bulk inserts — SQLite
  does them in one transaction, 100x faster than individual execute calls.
- **`row_factory = sqlite3.Row`**: Always set this. Without it, rows are plain
  tuples and you'll get cryptic positional bugs.
- **SQLite is not slow**: A properly indexed SQLite DB handles millions of rows
  comfortably. Most "SQLite is slow" issues are missing indexes.
- **Expression indexes on JSON**: `CREATE INDEX ... ON t(json_extract(col, '$.field'))`
  lets the query planner use the index for `WHERE json_extract(col, '$.field') = ?`.
