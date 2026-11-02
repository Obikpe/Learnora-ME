# Lesson 19: Reusable Python–SQL Workflows and Data Pipelines

## Purpose

A one-off query is useful, but data scientists need workflows that can be rerun reliably. This lesson turns isolated code into a small maintainable pipeline. We will use Python to orchestrate steps and SQL to perform database work.

## Learning outcomes

Organise code into functions and modules; separate configuration from logic; parameterise date ranges; validate data; use transactions; log workflow progress; make ingestion repeatable; and document limitations and assumptions.

## 1. What is a data pipeline?

A data pipeline is a repeatable sequence that moves or transforms data from a source to a destination. A simple analytical pipeline may:
1. Open a database.
2. Extract a defined period using SQL.
3. Validate the result.
4. Transform or aggregate it.
5. Save outputs.
6. Record whether the run succeeded.

A pipeline should be repeatable: running it again should not silently duplicate records or produce inconsistent outputs.

## 2. Separate responsibilities

A useful project layout:

```text
sql_data_science/
├── data/
│   └── learning.db
├── src/
│   ├── db.py          # connection creation and configuration
│   ├── load.py        # load_orders()
│   ├── validation.py  # validate_orders()
│   ├── transform.py   # build_regional_summary()
│   └── pipeline.py    # run() orchestration
├── outputs/
└── run_pipeline.py
```

- db.py opens configured connections.
- queries.py contains SQL statements or query functions.
- validation.py checks assumptions.
- pipeline.py orchestrates extraction and transformation.
- run_pipeline.py is the entry point.

For a small course project, these can initially live in one file. Separation becomes useful as the project grows.

## 3. Centralise database connection logic

```python
# db.py
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "learning.db"

def get_connection(read_only=False):
    if read_only:
        uri = f"file:{DB_PATH.as_posix()}?mode=ro"
        connection = sqlite3.connect(uri, uri=True)
    else:
        connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection
```

This uses a path relative to the source file rather than relying on the terminal's current working directory. URI paths with special characters may need URI encoding; for simple classroom paths this example is sufficient. Do not accept arbitrary user-supplied database paths without validation.

## 4. Parameterise analysis windows

```python
import pandas as pd
from db import get_connection

def load_orders(start_date, end_date):
    sql = """
        SELECT order_id, customer_id, order_date, amount, region
        FROM orders
        WHERE order_date >= ?
          AND order_date < ?
          AND status = ?
    """
    with get_connection(read_only=True) as connection:
        return pd.read_sql_query(
            sql,
            connection,
            params=(start_date, end_date, "completed")
        )
```

The end date is exclusive. This pattern avoids missing times late on the final date when timestamps are stored consistently. Validate that start_date is earlier than end_date and that both values use the expected format.

## 5. Validate before analysing

```python
def validate_orders(df):
    required = {"order_id", "customer_id", "order_date", "amount", "region"}
    missing_columns = required - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing columns: {sorted(missing_columns)}")

    if df["order_id"].duplicated().any():
        raise ValueError("Duplicate order IDs detected")

    if df["amount"].dropna().lt(0).any():
        raise ValueError("Negative order amount detected")

    if df["order_id"].isna().any():
        raise ValueError("Order ID cannot be missing")
```

Validation rules must reflect the data domain. Negative amounts might be legitimate if refunds are represented as negative transactions. If so, the rule should distinguish sales from refunds rather than reject all negative values.

## 6. Build an analytical transformation

```python
def build_regional_summary(df):
    return (
        df.groupby("region", dropna=False)
          .agg(
              order_count=("order_id", "nunique"),
              revenue=("amount", "sum"),
              average_order_value=("amount", "mean")
          )
          .reset_index()
    )
```

The `nunique` choice is deliberate: it counts distinct order IDs. If the source is guaranteed one row per order, count rows may be equivalent. If the source has line items, they are not equivalent.

## 7. Persist outputs deliberately

```python
def save_summary(summary, connection):
    summary.to_sql(
        "regional_summary",
        connection,
        if_exists="replace",
        index=False
    )
```

This is acceptable for a disposable teaching output table. In a robust workflow, define the destination schema, validate output columns and use a controlled replace strategy. If the table is consumed by another process, replacing it may break constraints or permissions. Consider writing to a staging table and swapping only after validation.

## 8. Orchestrate the pipeline

```python
import logging
from load import load_orders
from validation import validate_orders
from transform import build_regional_summary
from db import get_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

def run(start_date, end_date):
    logging.info("Loading orders")
    orders = load_orders(start_date, end_date)

    logging.info("Validating %s rows", len(orders))
    validate_orders(orders)

    summary = build_regional_summary(orders)

    logging.info("Writing regional summary")
    with get_connection() as connection:
        summary.to_sql(
            "regional_summary",
            connection,
            if_exists="replace",
            index=False
        )

    logging.info("Pipeline completed")
    return summary
```

The imports assume you have organised the functions into the named modules. If you keep the code in one file, remove those imports and define the functions above run(). Logging records progress without printing every row.

## 9. Idempotency and repeatability

A pipeline is idempotent when repeating the same operation produces the same intended state rather than duplicating effects. Strategies include:
- Use stable source IDs and unique constraints.
- Use INSERT ... ON CONFLICT carefully when supported and appropriate.
- Load into a staging table, validate, then replace or merge.
- Record the processed source period.
- Avoid relying on “append” unless duplicate prevention is designed.

SQLite supports UPSERT syntax in modern versions. Understand the conflict target and update behaviour before using it. Do not use INSERT OR REPLACE casually: SQLite's REPLACE conflict algorithm can delete the conflicting row before inserting a replacement, which can affect foreign keys and triggers.

## 10. Reproducibility and documentation

Record:
- Database and SQLite versions.
- Input period and filters.
- Query and transformation definitions.
- Row counts before and after filtering.
- Validation checks and their results.
- Output table names and timestamp of run.
- Known limitations and assumptions.

Never put passwords or secrets in source code. For a local SQLite exercise, there may be no database password, but real systems require secure credential handling and access controls.

## Guided exercises

1. Move connection logic into a reusable function.
2. Write a function that extracts orders between two dates.
3. Add validation for duplicate IDs and missing required fields.
4. Create a regional summary with Pandas.
5. Save output to a destination table.
6. Add logging for each stage.
7. Run the pipeline twice and verify that output does not accumulate duplicate rows.

## Independent practice

Build a complete script that extracts a defined date range, validates the input, calculates monthly and regional metrics, writes results to the database and logs the run. Make the date range configurable. Include a short README with setup instructions, metric definitions, expected tables and known limitations.

## Summary

A useful SQL/Python workflow is repeatable, validated and documented. Python orchestrates; SQL retrieves and transforms relational data; Pandas supports analysis; transactions and idempotent design protect outputs. The next lesson combines the entire course into a final project.