# Lesson 15: Query Performance and Optimisation

## Learning outcomes

Explain how a query is planned and executed; recognise table scans and index searches; write efficient filters and joins; avoid unnecessary data transfer; interpret EXPLAIN QUERY PLAN; and benchmark queries carefully.

## 1. Why performance matters

A correct query can still be inefficient. A slow query wastes time and resources, and may prevent an analysis from being repeated on larger data. Optimisation means improving execution while preserving the intended result. Never make a query faster by silently changing its meaning.

## 2. Logical query structure and physical execution

SQL is declarative: you describe the result, not every physical step. The query optimiser chooses an execution plan. A simplified logical model is:
1. Identify source tables in FROM and JOIN.
2. Apply row filtering with WHERE.
3. Form groups and calculate aggregates.
4. Apply HAVING to groups.
5. Calculate selected expressions.
6. Apply DISTINCT if requested.
7. Sort and limit the final result.

This is a conceptual model, not a promise about the engine's physical execution order. The optimiser may reorder joins or push filters down when semantics allow.

## 3. SELECT only what you need

Prefer:

```sql
SELECT order_id, order_date, amount
FROM orders
WHERE customer_id = ?;
```

over SELECT * when only three columns are needed. This reduces data transferred to Python and makes the output contract explicit. It can also allow a covering index in suitable cases.

## 4. Filter early and correctly

A selective condition can reduce the rows processed by later operations. Avoid wrapping an indexed column in a function if a direct range predicate expresses the same requirement and allows index use.

For example, instead of:

```sql
WHERE strftime('%Y', order_date) = '2026'
```

a range can be preferable when dates are consistently stored in ISO format:

```sql
WHERE order_date >= '2026-01-01'
  AND order_date < '2027-01-01'
```

This half-open range includes all dates in 2026 without guessing the final timestamp of the year. The comparison is reliable only if the stored values use a consistent sortable representation.

## 5. Indexes and query patterns

An index can help with equality filters, range filters, joins and ordering. A composite index should reflect common leading conditions. For example, an index on `(customer_id, order_date)` can help queries filtering a customer and restricting dates. It may also help customer-only filters, but not necessarily date-only filters.

Do not create an index for every column. Measure the workload and consider write frequency, table size, selectivity and storage.

## 6. Inspect the plan

```sql
EXPLAIN QUERY PLAN
SELECT order_id, amount
FROM orders
WHERE customer_id = 42;
```

In Python:

```python
import sqlite3

with sqlite3.connect("data/learning.db") as connection:
    for row in connection.execute("""
        EXPLAIN QUERY PLAN
        SELECT order_id, amount
        FROM orders
        WHERE customer_id = ?
    """, (42,)):
        print(row)
```

SQLite may report SCAN or SEARCH and may identify an index. A SCAN is not always bad: reading a tiny table or most of a table can make a scan reasonable. The plan must be interpreted in context.

## 7. Join efficiency

Join columns should have compatible meanings and types. Primary keys are indexed automatically in typical SQLite table definitions; foreign-key columns are not automatically indexed just because they are declared as foreign keys. Index child-side foreign keys when query patterns or parent updates/deletes make that useful.

Avoid joining tables before reducing them when the question only needs a summary. But do not pre-aggregate if that changes the required grain. Confirm that each join preserves the intended meaning.

## 8. Avoid unnecessary work in Python

If SQL can filter a million records down to a thousand, perform that filter in the database rather than loading all million rows into Pandas and filtering afterwards. Transfer only necessary columns. For genuinely large result sets, fetch in chunks rather than using fetchall.

```python
cursor = connection.execute(
    "SELECT order_id, amount FROM orders WHERE order_date >= ?",
    ("2026-01-01",)
)
while batch := cursor.fetchmany(1000):
    process(batch)
```

This pattern bounds the number of rows held in each batch. The `process` function is illustrative; define it for your workflow.

## 9. Benchmarking responsibly

Measure more than once. Use representative data, the same machine, comparable cache conditions and the same query output. Separate query execution time from Python printing and file I/O. Avoid timing a tiny dataset and claiming performance at scale. SQLite's EXPLAIN QUERY PLAN explains strategy; timing measures observed performance.

## 10. Maintainable SQL

Readable SQL is easier to optimise and less likely to contain hidden errors:
- Use descriptive aliases.
- Select explicit columns.
- Format clauses consistently.
- Break complex work into CTEs.
- Document metric definitions and assumptions.
- Keep parameter values separate from SQL text.
- Verify row counts and aggregates before and after a rewrite.

## Guided exercises

1. Inspect a query plan for a filter before and after adding an index.
2. Compare SELECT * with selecting two columns.
3. Rewrite a year filter as a date range.
4. Create an index that supports a customer/date query.
5. Compare a table scan and index search on a larger synthetic table.
6. Fetch results in batches and compare memory behaviour conceptually with fetchall.

## Independent practice

Generate at least 50,000 synthetic orders using Python. Write a customer/date query, inspect its query plan, create a suitable composite index and inspect again. Measure repeated runs and record the database version, row count, index definition and observed timings. Explain why the result may differ on another machine.

## Summary

Optimisation is a measured process. Select only needed columns, filter with appropriate predicates, understand indexes, inspect query plans, avoid unnecessary data transfer and preserve the meaning of the analysis. A scan is not automatically bad, and an index is not automatically beneficial.

## Next lesson

You have now learned the main SQL concepts. From the next lesson onward, we focus directly on the Python database workflow: connections, cursors, execution, parameter binding and results.