# Lesson 06: Aggregation and Grouped Analysis

## Why aggregation matters

Most analytical questions are not about one record. They ask for totals, averages, counts, proportions or comparisons across groups. Aggregation turns many row-level observations into a smaller summary.

## Learning outcomes

Use `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`; distinguish row counts from non-NULL counts; group rows with `GROUP BY`; filter groups with `HAVING`; use conditional aggregation; and explain common grouping errors.

## 1. Aggregate functions

Assume an `orders` table with `order_id`, `customer_id`, `region`, `order_date` and `amount`.

- `COUNT(*)` counts rows.
- `COUNT(column)` counts non-NULL values in that column.
- `SUM(amount)` adds non-NULL amounts.
- `AVG(amount)` calculates the arithmetic mean of non-NULL amounts.
- `MIN(amount)` and `MAX(amount)` return the smallest and largest non-NULL values.

Example:

```sql
SELECT
    COUNT(*) AS number_of_orders,
    COUNT(amount) AS orders_with_amount,
    SUM(amount) AS total_revenue,
    AVG(amount) AS average_order_value,
    MIN(amount) AS smallest_order,
    MAX(amount) AS largest_order
FROM orders;
```

This query has no GROUP BY, so it produces one summary row for the whole input table. If the table is empty, aggregate behaviour still needs consideration: COUNT returns zero, while SUM/AVG/MIN/MAX may return NULL.

## 2. Why COUNT(*) and COUNT(column) differ

Suppose five orders exist but one has a missing amount. `COUNT(*)` returns five because five rows exist. `COUNT(amount)` returns four because only four amount values are present. This difference is useful for data-quality checks. Never assume a count of a field equals the number of records.

## 3. GROUP BY

To calculate a total per region:

```sql
SELECT
    region,
    SUM(amount) AS regional_revenue
FROM orders
GROUP BY region;
```

The database partitions rows into groups with the same region value, then calculates the aggregate for each group. A NULL region, if present, forms its own group.

Think of the operation as:
1. Read the rows.
2. Place rows with matching region values into the same group.
3. Calculate the sum within each group.
4. Return one result row per group.

You can group by more than one field:

```sql
SELECT region, strftime('%Y', order_date) AS order_year,
       SUM(amount) AS revenue
FROM orders
GROUP BY region, strftime('%Y', order_date);
```

Each unique region/year combination becomes a group.

## 4. HAVING versus WHERE

`WHERE` filters individual rows before grouping. `HAVING` filters groups after aggregate values have been calculated.

```sql
SELECT region, SUM(amount) AS revenue
FROM orders
WHERE order_date >= '2026-01-01'
GROUP BY region
HAVING SUM(amount) >= 100000;
```

First, only orders from the date range remain. Then the database groups those orders by region. Finally, it keeps groups whose total is at least 100,000.

A common mistake is trying to use an aggregate in WHERE. Use HAVING for a condition on an aggregate result.

## 5. Conditional aggregation

You can calculate several metrics from the same group using CASE inside aggregate functions:

```sql
SELECT
    region,
    COUNT(*) AS all_orders,
    SUM(CASE WHEN amount >= 50000 THEN 1 ELSE 0 END) AS high_value_orders,
    SUM(CASE WHEN amount < 50000 THEN 1 ELSE 0 END) AS lower_value_orders,
    SUM(CASE WHEN amount >= 50000 THEN amount ELSE 0 END) AS high_value_revenue
FROM orders
GROUP BY region;
```

This is often more efficient and clearer than issuing many separate queries. The CASE expression returns 1 or 0 for each row, and SUM counts the qualifying rows.

## 6. Ratios and percentages

A percentage is a numerator divided by a denominator, multiplied by 100. Use a floating-point factor to avoid integer division surprises:

```sql
SELECT
    region,
    100.0 * SUM(CASE WHEN amount >= 50000 THEN 1 ELSE 0 END)
        / COUNT(*) AS high_value_order_pct
FROM orders
GROUP BY region;
```

Always define the denominator. Is the percentage of all orders, orders with a known amount, customers, or revenue? A mathematically correct percentage can still answer the wrong question if its denominator is poorly chosen. Protect against division by zero when a denominator can be zero.

## 7. NULL and aggregate interpretation

Most aggregate functions ignore NULL values. AVG(amount), for example, averages the known amounts, not all rows with missing values treated as zero. Replacing missing amounts with zero changes the meaning and should only happen when zero is a justified business interpretation.

## 8. Query results in Python

```python
import sqlite3

with sqlite3.connect("data/learning.db") as connection:
    rows = connection.execute("""
        SELECT region, COUNT(*) AS order_count,
               ROUND(SUM(amount), 2) AS revenue
        FROM orders
        GROUP BY region
        ORDER BY revenue DESC
    """).fetchall()

for region, order_count, revenue in rows:
    print(region, order_count, revenue)
```

Python receives the grouped result as tuples. Later, we will place this result directly into a Pandas DataFrame.

## Guided exercises

1. Count all orders.
2. Count orders with a known amount.
3. Calculate total and average amount.
4. Calculate revenue per region.
5. Show only regions with at least five orders.
6. Calculate the percentage of orders above a threshold per region.
7. Compare the result of filtering dates in WHERE with filtering groups in HAVING.

## Independent practice

Create a `sales` table with at least 20 rows, three regions, several product categories and a few NULL values. Produce a report with total sales, order count, average order value and high-value order percentage by region and category. Explain the denominator used for every percentage and how NULL values affect the metrics.

## Common mistakes

- Selecting a non-aggregated column that is not part of the GROUP BY. SQLite may allow some ambiguous aggregate queries, but do not rely on that permissiveness; write portable, unambiguous SQL.
- Using WHERE to filter aggregate results.
- Treating NULL as zero without justification.
- Forgetting that COUNT(column) excludes NULL.
- Calculating percentages without defining the denominator.

## Summary

Aggregate functions summarise rows. GROUP BY creates groups; HAVING filters those groups. Conditional aggregation calculates several related measures in one pass. Interpretation of NULL values and denominators is part of analytical correctness.

## Next lesson

To join tables reliably, you must understand why databases separate entities and how keys express relationships. We will design a small relational schema.