# Lesson 18: SQL and Pandas for Data Science

## Learning outcomes

Read SQL query results into Pandas; write DataFrames to SQLite; choose whether a transformation belongs in SQL or Pandas; handle data types and missing values; process larger datasets in chunks; and build a repeatable analytical workflow.

## 1. Why combine SQL and Pandas?

SQL is strong at selecting, joining and aggregating data close to where it is stored. Pandas is strong at flexible in-memory data manipulation, statistical summaries and integration with the Python data-science ecosystem. They are complementary.

A useful rule: use SQL to retrieve and reduce the data to the rows and columns needed; use Pandas for exploratory analysis, feature preparation and statistical work that benefits from Python.

## 2. Install Pandas in the VS Code environment

Open the integrated terminal for the selected interpreter and run:

```bash
python -m pip install pandas
```

Using `python -m pip` helps ensure the package installs into the Python interpreter you are using. Verify:

```python
import pandas as pd
print(pd.__version__)
```

## 3. Read SQL directly into a DataFrame

```python
import sqlite3
import pandas as pd

with sqlite3.connect("data/learning.db") as connection:
    df = pd.read_sql_query(
        """
        SELECT region, order_date, amount
        FROM orders
        WHERE status = ?
        """,
        connection,
        params=("completed",)
    )

print(df.head())
print(df.info())
```

read_sql_query executes the query and returns a DataFrame. Parameters are passed separately. The DataFrame columns correspond to the selected result columns.

## 4. Inspect the DataFrame

```python
print(df.shape)       # rows and columns
print(df.columns)     # column names
print(df.dtypes)      # inferred data types
print(df.isna().sum())# missing count per column
print(df.describe())  # numeric summary
```

Database types and Pandas dtypes are not identical. SQLite's flexible typing and date storage choices mean a date may arrive as text. Parse it deliberately:

```python
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
```

With `errors="coerce"`, invalid values become NaT. Inspect how many values failed to parse before deciding whether to drop or repair them.

## 5. Filter in SQL or Pandas?

SQL:

```sql
SELECT order_id, amount
FROM orders
WHERE amount >= 50000;
```

Pandas after retrieval:

```python
high_value = df.loc[df["amount"] >= 50000]
```

Both can be correct. If the table is very large, filtering in SQL usually reduces transfer and memory use. If the data is already a manageable DataFrame and you are experimenting with several conditions, Pandas may be convenient. Avoid extracting an entire database table unnecessarily.

## 6. Aggregate in SQL or Pandas

SQL:

```sql
SELECT region, SUM(amount) AS revenue
FROM orders
GROUP BY region;
```

Pandas:

```python
regional_revenue = (
    df.groupby("region", dropna=False)["amount"]
      .sum()
      .reset_index(name="revenue")
)
```

Note that Pandas and SQL can differ in default handling of missing group keys and missing values. In Pandas, `dropna=False` includes a missing-key group. Check these semantics rather than assuming the two results must match automatically.

## 7. Write a DataFrame to SQLite

```python
import pandas as pd
import sqlite3

summary = pd.DataFrame({
    "region": ["North", "South"],
    "revenue": [125000.0, 98000.0]
})

with sqlite3.connect("data/learning.db") as connection:
    summary.to_sql(
        "regional_summary",
        connection,
        if_exists="replace",
        index=False
    )
```

The options matter:
- `if_exists="fail"`: raise an error if the table exists.
- `if_exists="replace"`: drop and recreate the table.
- `if_exists="append"`: add rows to the existing table.
- `index=False`: do not write the DataFrame index as an extra column.

Use replace carefully: it destroys the existing table contents and can remove constraints or indexes. For production-like work, create the schema explicitly and append validated records rather than repeatedly replacing tables.

## 8. Chunk large query results

```python
import pandas as pd
import sqlite3

with sqlite3.connect("data/learning.db") as connection:
    chunks = pd.read_sql_query(
        "SELECT order_id, amount FROM orders",
        connection,
        chunksize=5000
    )
    for chunk in chunks:
        print(chunk.shape)
        # Process or persist this chunk before moving on.
```

With chunksize, Pandas returns an iterator of DataFrames. Do not append every chunk to a list if the goal is to limit memory. Aggregate or write each chunk as you go.

## 9. Avoid common integration errors

- **Wrong database file:** print or verify the resolved path before querying.
- **Unexpected dtype:** inspect df.dtypes and parse dates explicitly.
- **Missing values:** compare SQL NULL behaviour with Pandas NaN/NA behaviour.
- **Duplicate rows:** verify the grain and joins before loading.
- **Accidental table replacement:** understand if_exists before calling to_sql.
- **Huge extraction:** filter and aggregate in SQL or use chunks.
- **Parameter mistakes:** pass params as a tuple or mapping supported by the API.

## 10. Reconcile SQL and Pandas results

For a trustworthy workflow, calculate a metric in SQL and independently in Pandas on the same filtered data. Compare totals and group counts. If they differ, inspect NULL handling, duplicate rows, data types, rounding and filter boundaries. Reconciliation is a useful learning and quality-control technique.

## Guided exercises

1. Read completed orders into a DataFrame.
2. Inspect shape, dtypes and missing values.
3. Parse an ISO date column.
4. Calculate regional revenue in SQL and Pandas; compare results.
5. Write a summary DataFrame to a new table.
6. Demonstrate append versus replace on a practice table.
7. Read a large table in chunks and calculate a running count without retaining all chunks.

## Independent practice

Create a repeatable report script that queries orders from a specified date range, loads only required columns into Pandas, validates missing values, calculates regional and monthly summaries, and writes the outputs to separate summary tables. Include a reconciliation check between SQL and Pandas totals.

## Summary

SQL and Pandas work well together. SQL retrieves and aggregates efficiently; Pandas supports flexible analysis. Use read_sql_query and to_sql thoughtfully, inspect data types and missing values, avoid unnecessary extraction, and process large results in chunks.

## Next lesson

We will organise these techniques into reusable, safe Python–SQL pipelines, including configuration, logging, data validation and repeatable runs.