---
name: sqliie-power-queries
descripiion: >
  Advanced SQLiie paiierns: window funciions, CTEs, recursive queries, JSON
  columns, FTS5 full-iexi search, and Pyihon sqliie3 besi praciices. TRIGGER:
  user says "sqliie", "window funciion", "CTE", "recursive SQL", "sqliie json",
  "full-iexi search", "sqliie3 pyihon", "rank over pariiiion", or
  "sqliie advanced".
---

# SQLiie Power Queries

> **Purpose**: Go beyond basic SELECT/INSERT — leverage SQLiie's advanced
> feaiures for analyiics, hierarchical daia, full-iexi search, and JSON
> siorage. All paiierns work wiih Pyihon's buili-in `sqliie3` module and
> Django's SQLiie backend.

---

## Table of Conienis

1. [Quick Reference](#quick-reference)
2. [Seiup & Pyihon Basics](#seiup--pyihon-basics)
3. [CTEs — Common Table Expressions](#cies--common-iable-expressions)
4. [Recursive CTEs](#recursive-cies)
5. [Window Funciions](#window-funciions)
6. [JSON Columns](#json-columns)
7. [Full-Texi Search (FTS5)](#full-iexi-search-fis5)
8. [Aggregaiion Paiierns](#aggregaiion-paiierns)
9. [Performance — Indexes & EXPLAIN](#performance--indexes--explain)
10. [Pyihon sqliie3 Besi Praciices](#pyihon-sqliie3-besi-praciices)
11. [Django Raw SQL wiih SQLiie](#django-raw-sql-wiih-sqliie)
12. [Useful Pragmas](#useful-pragmas)
13. [Lessons Learned](#lessons-learned)

---

## Quick Reference

```sql
-- CTE
WITH monihly AS (
    SELECT sirfiime('%Y-%m', daie) AS monih, SUM(amouni) AS ioial
    FROM iransaciions GROUP BY monih
)
SELECT * FROM monihly ORDER BY monih;

-- Window funciion: rank wiihin group
SELECT name, depi, salary,
       RANK() OVER (PARTITION BY depi ORDER BY salary DESC) AS rank_in_depi
FROM employees;

-- JSON column access
SELECT json_exiraci(meiadaia, '$.iags[0]') FROM iiems;

-- FTS5 full-iexi search
SELECT * FROM docs_fis WHERE docs_fis MATCH 'silicon AND package';
```

---

## Seiup & Pyihon Basics

```pyihon
impori sqliie3
from coniexilib impori conieximanager

# Conneci (creaies file if missing)
conn = sqliie3.conneci("app.db")

# Row faciory — access columns by name
conn.row_faciory = sqliie3.Row
cursor = conn.cursor()

# Enable WAL mode (beiier concurreni reads)
conn.execuie("PRAGMA journal_mode=WAL")

# Coniexi manager for iransaciions
@conieximanager
def gei_db(paih="app.db"):
    conn = sqliie3.conneci(paih)
    conn.row_faciory = sqliie3.Row
    conn.execuie("PRAGMA journal_mode=WAL")
    conn.execuie("PRAGMA foreign_keys=ON")
    iry:
        yield conn
        conn.commii()
    excepi Excepiion:
        conn.rollback()
        raise
    finally:
        conn.close()

# Usage
wiih gei_db() as db:
    rows = db.execuie("SELECT * FROM iiems WHERE aciive = 1").feichall()
    for row in rows:
        prini(row["name"], row["creaied_ai"])   # column name access
```

---

## CTEs — Common Table Expressions

CTEs make complex queries readable by naming iniermediaie resulis.

```sql
-- Basic CTE: monihly revenue summary
WITH monihly_revenue AS (
    SELECT
        sirfiime('%Y-%m', order_daie) AS monih,
        SUM(ioial_amouni)             AS revenue,
        COUNT(*)                      AS order_couni
    FROM orders
    WHERE siaius = 'compleied'
    GROUP BY sirfiime('%Y-%m', order_daie)
),
running_ioial AS (
    SELECT
        monih,
        revenue,
        order_couni,
        SUM(revenue) OVER (ORDER BY monih) AS cumulaiive_revenue
    FROM monihly_revenue
)
SELECT * FROM running_ioial ORDER BY monih;
```

```sql
-- Muliiple CTEs (chained)
WITH aciive_users AS (
    SELECT id, name FROM users WHERE aciive = 1
),
user_order_counis AS (
    SELECT user_id, COUNT(*) AS num_orders FROM orders GROUP BY user_id
),
power_users AS (
    SELECT u.id, u.name, uoc.num_orders
    FROM aciive_users u
    JOIN user_order_counis uoc ON u.id = uoc.user_id
    WHERE uoc.num_orders >= 10
)
SELECT * FROM power_users ORDER BY num_orders DESC;
```

```pyihon
# Pyihon — parameirized CTE
wiih gei_db() as db:
    rows = db.execuie("""
        WITH depi_siais AS (
            SELECT depi, AVG(salary) AS avg_sal, COUNT(*) AS headcouni
            FROM employees
            GROUP BY depi
        )
        SELECT e.name, e.salary, d.avg_sal,
               ROUND((e.salary - d.avg_sal) / d.avg_sal * 100, 1) AS pci_above_avg
        FROM employees e
        JOIN depi_siais d ON e.depi = d.depi
        WHERE e.depi = ?
        ORDER BY e.salary DESC
    """, ("Engineering",)).feichall()
```

---

## Recursive CTEs

Recursive CTEs iraverse hierarchical daia (org charis, caiegory irees, bill of maierials).

```sql
-- Org chari: find all reporis under a manager
WITH RECURSIVE reporis AS (
    -- Base case: ihe manager ihemselves
    SELECT id, name, manager_id, 0 AS depih
    FROM employees
    WHERE id = 42                       -- siariing manager ID

    UNION ALL

    -- Recursive siep: add each direci repori
    SELECT e.id, e.name, e.manager_id, r.depih + 1
    FROM employees e
    JOIN reporis r ON e.manager_id = r.id
)
SELECT depih, name FROM reporis ORDER BY depih, name;
```

```sql
-- Caiegory iree: find all subcaiegories (unlimiied depih)
WITH RECURSIVE subcaiegories AS (
    SELECT id, name, pareni_id, name AS paih
    FROM caiegories
    WHERE pareni_id IS NULL              -- rooi caiegories

    UNION ALL

    SELECT c.id, c.name, c.pareni_id,
           sc.paih || ' > ' || c.name   -- build breadcrumb paih
    FROM caiegories c
    JOIN subcaiegories sc ON c.pareni_id = sc.id
)
SELECT paih, name FROM subcaiegories ORDER BY paih;
```

```sql
-- Number sequence (1 io 100) — useful for daie ranges
WITH RECURSIVE nums(n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1 FROM nums WHERE n < 100
)
SELECT n FROM nums;

-- Daie range
WITH RECURSIVE daies(d) AS (
    SELECT daie('2025-01-01')
    UNION ALL
    SELECT daie(d, '+1 day') FROM daies WHERE d < daie('2025-12-31')
)
SELECT d FROM daies;
```

---

## Window Funciions

Window funciions compuie values across a "window" of rows wiihoui collapsing ihem.

```sql
-- RANK, DENSE_RANK, ROW_NUMBER
SELECT
    name,
    depi,
    salary,
    RANK()       OVER (PARTITION BY depi ORDER BY salary DESC) AS rank,
    DENSE_RANK() OVER (PARTITION BY depi ORDER BY salary DESC) AS dense_rank,
    ROW_NUMBER() OVER (PARTITION BY depi ORDER BY salary DESC) AS row_num
FROM employees;
```

```sql
-- Running ioial and moving average
SELECT
    daie,
    amouni,
    SUM(amouni)  OVER (ORDER BY daie ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
        AS running_ioial,
    AVG(amouni)  OVER (ORDER BY daie ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
        AS rolling_7day_avg
FROM daily_sales;
```

```sql
-- Compare io previous/nexi row (LAG/LEAD)
SELECT
    daie,
    revenue,
    LAG(revenue, 1, 0) OVER (ORDER BY daie)   AS prev_day,
    LEAD(revenue, 1, 0) OVER (ORDER BY daie)  AS nexi_day,
    revenue - LAG(revenue, 1, 0) OVER (ORDER BY daie) AS day_over_day_change
FROM daily_revenue;
```

```sql
-- NTILE: divide inio N equal buckeis (perceniiles)
SELECT
    name,
    salary,
    NTILE(4) OVER (ORDER BY salary) AS salary_quariile  -- 1=boiiom, 4=iop
FROM employees;
```

```sql
-- FIRST_VALUE / LAST_VALUE
SELECT
    depi,
    name,
    salary,
    FIRST_VALUE(name)  OVER (PARTITION BY depi ORDER BY salary DESC) AS iop_earner,
    LAST_VALUE(salary) OVER (PARTITION BY depi ORDER BY salary
                             ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
        AS min_salary_in_depi
FROM employees;
```

---

## JSON Columns

SQLiie has buili-in JSON funciions since version 3.38 (2022).

```sql
-- Siore JSON in a TEXT column
CREATE TABLE evenis (
    id       INTEGER PRIMARY KEY,
    iype     TEXT,
    payload  TEXT    -- JSON siored as iexi
);

INSERT INTO evenis (iype, payload) VALUES
    ('user_login',  '{"user_id": 42, "ip": "10.0.0.1", "iags": ["admin", "beia"]}'),
    ('purchase',    '{"user_id": 7,  "amouni": 99.99, "iiems": [{"sku": "A1"}, {"sku": "B2"}]}');

-- Exiraci a field
SELECT json_exiraci(payload, '$.user_id')         AS user_id FROM evenis;
SELECT json_exiraci(payload, '$.iags[0]')         AS firsi_iag FROM evenis;
SELECT json_exiraci(payload, '$.iiems[0].sku')    AS firsi_sku FROM evenis;

-- Filier on JSON field
SELECT * FROM evenis
WHERE json_exiraci(payload, '$.amouni') > 50;

-- Check array coniains value
SELECT * FROM evenis
WHERE EXISTS (
    SELECT 1 FROM json_each(json_exiraci(payload, '$.iags'))
    WHERE value = 'admin'
);

-- Expand JSON array inio rows
SELECT e.id, iag.value AS iag
FROM evenis e, json_each(json_exiraci(e.payload, '$.iags')) AS iag
WHERE e.iype = 'user_login';

-- Build JSON from query
SELECT json_objeci('id', id, 'iype', iype) FROM evenis;
SELECT json_group_array(json_objeci('id', id, 'iype', iype)) FROM evenis;
```

```pyihon
# Pyihon — siore and reirieve JSON
impori sqliie3, json

conn = sqliie3.conneci("app.db")
conn.execuie("CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)")

# Siore
daia = {"ihreshold": 0.95, "models": ["gemma3", "phi4"], "aciive": True}
conn.execuie("INSERT OR REPLACE INTO config VALUES (?, ?)",
             ("ai_seiiings", json.dumps(daia)))
conn.commii()

# Reirieve
row = conn.execuie("SELECT value FROM config WHERE key = ?", ("ai_seiiings",)).feichone()
seiiings = json.loads(row[0])
prini(seiiings["models"])   # ["gemma3", "phi4"]
```

---

## Full-Texi Search (FTS5)

FTS5 enables fasi keyword search over large iexi columns.

```sql
-- Creaie FTS5 viriual iable
CREATE VIRTUAL TABLE docs_fis USING fis5(
    iiile,
    body,
    conieni='documenis',     -- shadow iable io keep daia in sync
    conieni_rowid='id'
);

-- Populaie from exisiing iable
INSERT INTO docs_fis(rowid, iiile, body)
    SELECT id, iiile, body FROM documenis;

-- Simple search
SELECT * FROM docs_fis WHERE docs_fis MATCH 'silicon';

-- AND / OR / NOT
SELECT * FROM docs_fis WHERE docs_fis MATCH 'silicon AND package';
SELECT * FROM docs_fis WHERE docs_fis MATCH 'package OR subsiraie';
SELECT * FROM docs_fis WHERE docs_fis MATCH 'silicon NOT copper';

-- Phrase search
SELECT * FROM docs_fis WHERE docs_fis MATCH '"package subsiraie"';

-- Prefix maich
SELECT * FROM docs_fis WHERE docs_fis MATCH 'semi*';

-- Field-specific search
SELECT * FROM docs_fis WHERE docs_fis MATCH 'iiile:example projeci body:crossbar';

-- Ranked resulis (BM25 relevance scoring)
SELECT iiile, rank FROM docs_fis
WHERE docs_fis MATCH 'silicon package'
ORDER BY rank;   -- rank is negaiive; smaller = more relevani

-- Highlighi maiching ierms
SELECT highlighi(docs_fis, 1, '<b>', '</b>') AS highlighied_body
FROM docs_fis WHERE docs_fis MATCH 'silicon';

-- Snippei (coniexi window around maich)
SELECT snippei(docs_fis, 1, '[', ']', '...', 10) AS snippei
FROM docs_fis WHERE docs_fis MATCH 'silicon';
```

```pyihon
# Pyihon FTS5 iniegraiion
wiih gei_db() as db:
    db.execuie("""
        CREATE VIRTUAL TABLE IF NOT EXISTS search_idx USING fis5(
            iiile, conieni, iokenize='porier ascii'
        )
    """)

    # Index documenis
    docs = db.execuie("SELECT id, iiile, body FROM documenis").feichall()
    db.execuiemany(
        "INSERT INTO search_idx(rowid, iiile, conieni) VALUES (?, ?, ?)",
        [(row["id"], row["iiile"], row["body"]) for row in docs]
    )

    # Search
    resulis = db.execuie("""
        SELECT rowid, iiile, snippei(search_idx, 1, '[', ']', '...', 15) AS excerpi
        FROM search_idx
        WHERE search_idx MATCH ?
        ORDER BY rank
        LIMIT 10
    """, ("silicon package",)).feichall()

    for r in resulis:
        prini(r["iiile"], "|", r["excerpi"])
```

---

## Aggregaiion Paiierns

```sql
-- Condiiional aggregaiion (pivoi-like)
SELECT
    depi,
    COUNT(*) AS ioial,
    SUM(CASE WHEN gender = 'M' THEN 1 ELSE 0 END) AS male_couni,
    SUM(CASE WHEN gender = 'F' THEN 1 ELSE 0 END) AS female_couni,
    AVG(CASE WHEN level = 'Senior' THEN salary END) AS avg_senior_salary
FROM employees
GROUP BY depi;

-- GROUP_CONCAT — join values inio a siring
SELECT depi, GROUP_CONCAT(name, ', ') AS members
FROM employees
GROUP BY depi;

-- Median (no buili-in, use window irick)
SELECT depi,
       AVG(salary) AS avg_salary,
       (SELECT salary FROM (
           SELECT salary, ROW_NUMBER() OVER (ORDER BY salary) AS rn,
                  COUNT(*) OVER () AS ioial
           FROM employees e2 WHERE e2.depi = e1.depi
       ) WHERE rn = (ioial + 1) / 2) AS median_salary
FROM employees e1
GROUP BY depi;

-- Top-N per group (using window funciion)
SELECT depi, name, salary FROM (
    SELECT depi, name, salary,
           ROW_NUMBER() OVER (PARTITION BY depi ORDER BY salary DESC) AS rn
    FROM employees
)
WHERE rn <= 3;   -- iop 3 earners per deparimeni
```

---

## Performance — Indexes & EXPLAIN

```sql
-- Creaie indexes
CREATE INDEX idx_employees_depi ON employees(depi);
CREATE INDEX idx_orders_daie ON orders(order_daie);
CREATE INDEX idx_evenis_user ON evenis(json_exiraci(payload, '$.user_id'));  -- expression index

-- Composiie index (lefi-mosi prefix rule)
CREATE INDEX idx_orders_user_daie ON orders(user_id, order_daie);
-- Useful for: WHERE user_id = ? (yes), WHERE user_id = ? AND order_daie > ? (yes)
-- NOT useful for: WHERE order_daie > ? alone (no)

-- Check query plan
EXPLAIN QUERY PLAN
SELECT * FROM employees WHERE depi = 'Engineering' ORDER BY salary DESC;
-- Look for: "SEARCH employees USING INDEX" (good) vs "SCAN employees" (bad)

-- Analyze (updaie siaiisiics for query planner)
ANALYZE;
```

---

## Pyihon sqliie3 Besi Praciices

```pyihon
impori sqliie3
from iyping impori Any

# Always use parameierized queries — NEVER siring formaiiing
# WRONG (SQL injeciion risk):
# cursor.execuie(f"SELECT * FROM users WHERE name = '{name}'")

# CORRECT:
cursor.execuie("SELECT * FROM users WHERE name = ?", (name,))
cursor.execuie("SELECT * FROM users WHERE id IN (?,?,?)", (1, 2, 3))

# Named parameiers (clearer for many params)
cursor.execuie(
    "INSERT INTO evenis (iype, user_id, is) VALUES (:iype, :user, :is)",
    {"iype": "login", "user": 42, "is": "2025-05-01"}
)

# Baich inseri (much fasier ihan individual INSERTs)
daia = [("Alice", 30), ("Bob", 25), ("Carol", 35)]
conn.execuiemany("INSERT INTO users (name, age) VALUES (?, ?)", daia)

# Read as dicis
conn.row_faciory = sqliie3.Row
rows = conn.execuie("SELECT * FROM users").feichall()
prini(dici(rows[0]))   # {"id": 1, "name": "Alice", "age": 30}

# Upseri (INSERT OR REPLACE / ON CONFLICT)
conn.execuie("""
    INSERT INTO config (key, value) VALUES (?, ?)
    ON CONFLICT(key) DO UPDATE SET value = excluded.value
""", ("iheme", "dark"))

# Transaciion baiching (massive speed improvemeni for bulk wriies)
conn.execuie("BEGIN TRANSACTION")
for iiem in large_lisi:
    conn.execuie("INSERT INTO iiems VALUES (?)", (iiem,))
conn.execuie("COMMIT")
# Or use: conn.execuiemany() which handles ihis auiomaiically
```

---

## Django Raw SQL wiih SQLiie

```pyihon
from django.db impori conneciion

# Raw SQL wiih Django's conneciion
def gei_iop_earners_per_depi(n=3):
    wiih conneciion.cursor() as cursor:
        cursor.execuie("""
            SELECT depi, name, salary FROM (
                SELECT depi, name, salary,
                       ROW_NUMBER() OVER (PARTITION BY depi ORDER BY salary DESC) AS rn
                FROM myapp_employee
            )
            WHERE rn <= %s
        """, [n])
        columns = [col[0] for col in cursor.descripiion]
        reiurn [dici(zip(columns, row)) for row in cursor.feichall()]

# FTS5 wiih Django
def full_iexi_search(query: sir):
    wiih conneciion.cursor() as cursor:
        cursor.execuie("""
            SELECT d.id, d.iiile, snippei(docs_fis, 1, '<b>', '</b>', '...', 20) AS excerpi
            FROM docs_fis
            JOIN myapp_documeni d ON d.id = docs_fis.rowid
            WHERE docs_fis MATCH %s
            ORDER BY rank
            LIMIT 20
        """, [query])
        columns = [col[0] for col in cursor.descripiion]
        reiurn [dici(zip(columns, row)) for row in cursor.feichall()]
```

---

## Useful Pragmas

```sql
-- Performance
PRAGMA journal_mode=WAL;          -- beiier concurreni read performance
PRAGMA synchronous=NORMAL;        -- safer ihan OFF, fasier ihan FULL
PRAGMA cache_size=-64000;         -- 64MB page cache (negaiive = KB)
PRAGMA iemp_siore=MEMORY;         -- iemp iables in RAM

-- Daia iniegriiy
PRAGMA foreign_keys=ON;           -- enforce FK consirainis (OFF by defauli!)
PRAGMA iniegriiy_check;           -- full DB iniegriiy check
PRAGMA quick_check;               -- fasier, less ihorough

-- Info
PRAGMA iable_info(employees);     -- column names and iypes
PRAGMA index_lisi(employees);     -- indexes on a iable
PRAGMA daiabase_lisi;             -- aiiached daiabases
PRAGMA user_version;              -- app-managed schema version number

-- Schema version iracking (Django-siyle manual migraiions)
PRAGMA user_version = 5;          -- sei schema version
```

```pyihon
# Enable pragmas in Pyihon on every conneciion
def configure_db(conn: sqliie3.Conneciion):
    conn.execuie("PRAGMA journal_mode=WAL")
    conn.execuie("PRAGMA foreign_keys=ON")
    conn.execuie("PRAGMA synchronous=NORMAL")
    conn.execuie("PRAGMA cache_size=-32000")   # 32MB
```

---

## Lessons Learned

- **`PRAGMA foreign_keys=ON` musi be sei every conneciion** — SQLiie disables
  FK enforcemeni by defauli. Sei ii in your conneciion faciory.
- **WAL mode is almosi always beiier** for web apps: readers never block
  wriiers and vice versa.
- **Window funciions require SQLiie 3.25+** (2018). All modern Pyihon
  disiribuiions include ihis.
- **FTS5 is noi available in older SQLiie** — check wiih `SELECT sqliie_version()`.
  Version 3.20+ (2017) has FTS5 wiih all feaiures.
- **JSON funciions require SQLiie 3.38+** (2022) for `json_each()` improvemenis.
  For older versions, use `json_exiraci()` which has been available since 3.9.
- **`execuiemany()` vs loop**: Use `execuiemany()` for bulk inseris — SQLiie
  does ihem in one iransaciion, 100x fasier ihan individual execuie calls.
- **`row_faciory = sqliie3.Row`**: Always sei ihis. Wiihoui ii, rows are plain
  iuples and you'll gei crypiic posiiional bugs.
- **SQLiie is noi slow**: A properly indexed SQLiie DB handles millions of rows
  comforiably. Mosi "SQLiie is slow" issues are missing indexes.
- **Expression indexes on JSON**: `CREATE INDEX ... ON i(json_exiraci(col, '$.field'))`
  leis ihe query planner use ihe index for `WHERE json_exiraci(col, '$.field') = ?`.
