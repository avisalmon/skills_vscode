---
name: pandas-data-analysis
description: >
  Analyze and transform tabular data with pandas. Read CSV/Excel/JSON,
  filter and select data, group and aggregate, merge DataFrames, pivot
  tables, plot charts, handle missing values, work with time series,
  and export results. TRIGGER: user says "pandas", "dataframe", "read csv",
  "groupby", "pivot table", "data analysis", "merge dataframes", "filter
  rows", "plot data", or "data wrangling".
---

# Pandas Data Analysis

> **Purpose**: The complete Python toolkit for reading, transforming, analyzing,
> and visualizing tabular data. pandas 2.x / 3.x.

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Setup](#setup)
3. [Reading Data](#reading-data)
4. [Inspecting DataFrames](#inspecting-dataframes)
5. [Selecting & Filtering](#selecting--filtering)
6. [Adding & Transforming Columns](#adding--transforming-columns)
7. [Sorting](#sorting)
8. [Groupby & Aggregation](#groupby--aggregation)
9. [Pivot Tables](#pivot-tables)
10. [Merging & Joining](#merging--joining)
11. [Missing Values](#missing-values)
12. [String Operations](#string-operations)
13. [Time Series](#time-series)
14. [Exporting Data](#exporting-data)
15. [Plotting](#plotting)
16. [Performance Tips](#performance-tips)
17. [Lessons Learned](#lessons-learned)

---

## Quick Reference

```python
import pandas as pd
import numpy as np

df = pd.read_csv("data.csv")          # read
df.head()                              # preview
df.info()                              # schema
df.describe()                          # stats
df["col"]                              # single column (Series)
df[["col1", "col2"]]                   # multiple columns
df[df["age"] > 30]                     # filter rows
df.groupby("dept")["salary"].mean()    # groupby + agg
df.sort_values("salary", ascending=False)  # sort
df.merge(df2, on="id", how="left")     # join
df.pivot_table(values="sales", index="region", columns="year", aggfunc="sum")
df.to_csv("output.csv", index=False)   # export
```

---

## Setup

```powershell
pip install pandas openpyxl matplotlib
```

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pd.set_option("display.max_columns", None)   # show all columns
pd.set_option("display.width", 120)          # wider console output
pd.set_option("display.float_format", "{:.2f}".format)  # 2 decimal places
```

---

## Reading Data

### CSV
```python
df = pd.read_csv("data.csv")

# With options
df = pd.read_csv(
    "data.csv",
    sep=";",                      # semicolon delimiter
    encoding="utf-8",
    parse_dates=["date_col"],     # auto-parse date columns
    index_col="id",               # use column as index
    skiprows=1,                   # skip header row
    na_values=["N/A", "-", ""],   # treat these as NaN
)
```

### Excel
```python
df = pd.read_excel("data.xlsx")
df = pd.read_excel("data.xlsx", sheet_name="Sheet2")

# All sheets at once
sheets = pd.read_excel("data.xlsx", sheet_name=None)  # dict of DataFrames
for name, df in sheets.items():
    print(name, df.shape)
```

### JSON
```python
df = pd.read_json("data.json")
df = pd.read_json("data.json", orient="records")

# From API response
import requests
r = requests.get("https://api.example.com/data")
df = pd.DataFrame(r.json())
```

### From dict / list
```python
df = pd.DataFrame([
    {"name": "Alice", "age": 30, "dept": "Engineering"},
    {"name": "Bob",   "age": 25, "dept": "Sales"},
    {"name": "Carol", "age": 35, "dept": "Engineering"},
])
```

### From SQLite
```python
import sqlite3

conn = sqlite3.connect("db.sqlite3")
df = pd.read_sql_query("SELECT * FROM mytable WHERE active = 1", conn)
conn.close()
```

---

## Inspecting DataFrames

```python
df.head(10)           # first 10 rows
df.tail(5)            # last 5 rows
df.shape              # (rows, cols)
df.columns.tolist()   # column names as list
df.dtypes             # column data types
df.info()             # schema + non-null counts + memory
df.describe()         # stats: count, mean, std, min, quartiles, max
df.value_counts("col")  # frequency of each value in a column
df.nunique()          # count of unique values per column
df.isnull().sum()     # count of NaN per column
df.sample(5)          # random 5 rows
```

---

## Selecting & Filtering

### Column selection
```python
df["salary"]                # single column → Series
df[["name", "salary"]]      # multiple columns → DataFrame
df.iloc[:, 0:3]             # first 3 columns by position
df.loc[:, "name":"dept"]    # columns by name range (inclusive)
```

### Row filtering
```python
df[df["age"] > 30]                           # single condition
df[(df["age"] > 30) & (df["dept"] == "Engineering")]  # AND
df[(df["age"] < 25) | (df["dept"] == "Sales")]        # OR
df[~(df["dept"] == "Sales")]                 # NOT

df[df["dept"].isin(["Engineering", "HR"])]   # isin
df[df["name"].str.contains("Al", na=False)]  # string match

# By index
df.loc[0]                   # row by label/index
df.iloc[0]                  # row by position
df.iloc[0:5]                # rows 0-4 by position
df.loc[df["age"] > 30, ["name", "salary"]]  # rows + specific cols
```

### Query syntax (cleaner for complex filters)
```python
df.query("age > 30 and dept == 'Engineering'")
df.query("salary > @threshold")   # use Python variable with @
```

---

## Adding & Transforming Columns

```python
# New column from calculation
df["salary_k"] = df["salary"] / 1000
df["full_name"] = df["first"] + " " + df["last"]

# Conditional column
df["level"] = np.where(df["salary"] > 100000, "Senior", "Junior")

# Multiple conditions with np.select
conditions = [
    df["salary"] < 50000,
    df["salary"] < 100000,
    df["salary"] >= 100000,
]
choices = ["Junior", "Mid", "Senior"]
df["level"] = np.select(conditions, choices, default="Unknown")

# Apply a function
df["name_upper"] = df["name"].apply(str.upper)
df["bonus"] = df["salary"].apply(lambda x: x * 0.1 if x > 80000 else x * 0.05)

# Apply across multiple columns (axis=1)
df["full"] = df.apply(lambda row: f"{row['first']} {row['last']}", axis=1)

# Map values (replace)
mapping = {"M": "Male", "F": "Female"}
df["gender"] = df["gender"].map(mapping)

# Rename columns
df = df.rename(columns={"old_name": "new_name", "emp_id": "id"})

# Drop columns
df = df.drop(columns=["col_to_remove", "another"])
```

---

## Sorting

```python
df.sort_values("salary")                            # ascending
df.sort_values("salary", ascending=False)           # descending
df.sort_values(["dept", "salary"], ascending=[True, False])  # multi-column
df.sort_values("salary", inplace=True)              # modify in place
df.sort_index()                                      # by index
```

---

## Groupby & Aggregation

```python
# Single aggregation
df.groupby("dept")["salary"].mean()
df.groupby("dept")["salary"].sum()
df.groupby("dept")["salary"].count()
df.groupby("dept")["salary"].agg(["mean", "min", "max", "count"])

# Multiple columns, multiple aggregations
df.groupby("dept").agg(
    avg_salary=("salary", "mean"),
    headcount=("name", "count"),
    max_salary=("salary", "max"),
)

# Multiple groupby keys
df.groupby(["dept", "level"])["salary"].mean()

# Transform (keep original row count, add group stat as new column)
df["dept_avg_salary"] = df.groupby("dept")["salary"].transform("mean")
df["salary_vs_dept"] = df["salary"] - df["dept_avg_salary"]

# Filter groups (keep groups where count > 5)
df = df.groupby("dept").filter(lambda g: len(g) > 5)
```

---

## Pivot Tables

```python
# Sum of sales by region (rows) and year (columns)
pivot = df.pivot_table(
    values="sales",
    index="region",
    columns="year",
    aggfunc="sum",
    fill_value=0,      # replace NaN with 0
    margins=True,      # add row/col totals
)

# Multiple aggregations
pivot = df.pivot_table(
    values="sales",
    index="region",
    columns="product",
    aggfunc={"sales": "sum", "quantity": "mean"},
)

# Flatten multi-level column names
pivot.columns = ["_".join(map(str, c)) for c in pivot.columns]
```

---

## Merging & Joining

```python
# Inner join (only matching rows)
result = df1.merge(df2, on="id")

# Left join (keep all rows from df1)
result = df1.merge(df2, on="id", how="left")

# Merge on different column names
result = df1.merge(df2, left_on="emp_id", right_on="employee_id")

# Multiple join keys
result = df1.merge(df2, on=["dept", "year"])

# Stack DataFrames vertically (same columns)
combined = pd.concat([df1, df2, df3], ignore_index=True)

# Side by side (same rows, different columns)
combined = pd.concat([df1, df2], axis=1)
```

---

## Missing Values

```python
df.isnull().sum()              # count NaN per column
df.isnull().sum() / len(df)    # percentage NaN

# Drop rows/columns with NaN
df.dropna()                    # drop rows with ANY NaN
df.dropna(subset=["salary"])   # drop rows with NaN in specific column
df.dropna(axis=1)              # drop columns with ANY NaN
df.dropna(thresh=3)            # keep rows with at least 3 non-NaN values

# Fill NaN
df["salary"].fillna(0)
df["salary"].fillna(df["salary"].mean())
df["dept"].fillna("Unknown")
df.fillna({"salary": 0, "dept": "Unknown"})

# Forward / backward fill (for time series)
df["price"].ffill()   # fill with previous value
df["price"].bfill()   # fill with next value
```

---

## String Operations

```python
# All string ops live under .str accessor
df["name"].str.lower()
df["name"].str.upper()
df["name"].str.strip()
df["name"].str.replace("  ", " ")
df["name"].str.contains("Ali")
df["name"].str.startswith("A")
df["name"].str.split(" ")                         # split into list
df["name"].str.split(" ", expand=True)            # split into columns
df["name"].str.len()                              # string length
df["email"].str.extract(r"@(.+)$")               # regex extract
df["code"].str.zfill(6)                           # pad with zeros
```

---

## Time Series

```python
# Parse dates on read
df = pd.read_csv("data.csv", parse_dates=["date"])

# Convert column to datetime
df["date"] = pd.to_datetime(df["date"])
df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y")

# Extract components
df["year"]  = df["date"].dt.year
df["month"] = df["date"].dt.month
df["day"]   = df["date"].dt.day
df["dow"]   = df["date"].dt.day_name()    # "Monday", "Tuesday"...
df["week"]  = df["date"].dt.isocalendar().week

# Filter by date range
df[df["date"] >= "2025-01-01"]
df[(df["date"] >= "2025-01-01") & (df["date"] < "2026-01-01")]

# Resample (aggregate by time period)
df.set_index("date").resample("ME")["sales"].sum()   # monthly totals
df.set_index("date").resample("W")["sales"].mean()   # weekly average
df.set_index("date").resample("QE")["revenue"].sum() # quarterly

# Rolling window
df["rolling_7d"] = df.set_index("date")["sales"].rolling("7D").mean()
```

---

## Exporting Data

```python
# CSV
df.to_csv("output.csv", index=False)
df.to_csv("output.csv", index=False, encoding="utf-8-sig")  # with BOM for Excel

# Excel
df.to_excel("output.xlsx", index=False)
df.to_excel("output.xlsx", index=False, sheet_name="Results")

# Multiple sheets
with pd.ExcelWriter("output.xlsx") as writer:
    df1.to_excel(writer, sheet_name="Summary", index=False)
    df2.to_excel(writer, sheet_name="Detail",  index=False)

# JSON
df.to_json("output.json", orient="records", indent=2)

# Dict / list (for use in Python)
records = df.to_dict(orient="records")   # list of dicts
```

---

## Plotting

```python
import matplotlib.pyplot as plt

# Bar chart
df.groupby("dept")["salary"].mean().plot(kind="bar", title="Avg Salary by Dept")
plt.tight_layout()
plt.savefig("bar.png")
plt.show()

# Line chart
df.set_index("date")["sales"].plot(kind="line", title="Sales Over Time")

# Histogram
df["salary"].plot(kind="hist", bins=20, title="Salary Distribution")

# Scatter
df.plot(kind="scatter", x="age", y="salary", title="Age vs Salary")

# Box plot
df.boxplot(column="salary", by="dept")

# Correlation heatmap (requires seaborn)
import seaborn as sns
sns.heatmap(df.corr(), annot=True, fmt=".2f", cmap="coolwarm")
plt.show()
```

---

## Performance Tips

```python
# Check memory usage
df.memory_usage(deep=True).sum() / 1e6  # MB

# Downcast numeric types to save memory
df["age"] = pd.to_numeric(df["age"], downcast="integer")
df["price"] = pd.to_numeric(df["price"], downcast="float")

# Use categories for low-cardinality string columns
df["dept"] = df["dept"].astype("category")

# Read only needed columns
df = pd.read_csv("big.csv", usecols=["name", "salary", "dept"])

# Read in chunks for huge files
for chunk in pd.read_csv("huge.csv", chunksize=100_000):
    process(chunk)

# Use .apply() sparingly — vectorized operations are 10-100x faster
# BAD:
df["x2"] = df["x"].apply(lambda v: v * 2)
# GOOD:
df["x2"] = df["x"] * 2

# Use query() for readable filtering
df.query("age > 30 and dept == 'Engineering'")
```

---

## Lessons Learned

- **`inplace=True` is deprecated** in pandas 3.x for many operations. Prefer
  assignment: `df = df.dropna()` instead of `df.dropna(inplace=True)`.
- **Copy vs view**: `df[df["x"] > 0]["y"] = 1` may silently fail (SettingWithCopyWarning).
  Use `df.loc[df["x"] > 0, "y"] = 1` instead.
- **`read_excel` needs openpyxl**: `pip install openpyxl` — not bundled with pandas.
- **`parse_dates` is fast**: Pass column names to `read_csv(..., parse_dates=["date"])`
  rather than calling `pd.to_datetime()` after.
- **Category dtype**: For string columns with < 50 unique values, converting to
  `category` can reduce memory by 10x and speed up groupby.
- **`groupby` returns a new object**: Always assign the result.
  `df.groupby("x")` by itself does nothing visible.
- **Excel export**: Use `index=False` almost always — the default index (0, 1, 2...)
  adds an unwanted column.
- **`.str` accessor handles NaN**: Most `.str` methods return NaN for NaN inputs
  without raising errors. Pass `na=False` to `.str.contains()` to get False instead.
