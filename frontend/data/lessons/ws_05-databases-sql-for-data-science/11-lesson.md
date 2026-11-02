# Lesson 11: Window Functions for Analytical SQL

## Learning outcomes

Explain the difference between grouped aggregation and window calculations; use OVER, PARTITION BY and ORDER BY; apply ROW_NUMBER, RANK and DENSE_RANK; calculate running totals and moving averages; and compare rows using LAG and LEAD.

## 1. Why window functions?

GROUP BY collapses many rows into one row per group. Sometimes you need a group-level calculation while keeping every original row. Window functions do exactly that: they calculate across a related set of rows (the *window*) while preserving the rows in the result.

Suppose you have monthly sales by region. GROUP BY can produce one row per region and month. A window function can add a running total to each monthly row without collapsing the months.

## 2. The OVER clause

```sql
SELECT
    order_id,
    region,
    amount,
    SUM(amount) OVER () AS all_order_total
FROM orders;
```

The empty OVER clause defines one window containing all rows in the query result. Each row receives the same total, but all order rows remain visible.

## 3. PARTITION BY

```sql
SELECT
    order_id,
    region,
    amount,
    SUM(amount) OVER (PARTITION BY region) AS region_total
FROM orders;
```

PARTITION BY divides the rows into independent windows. Each region gets its own total. Unlike GROUP BY, it does not reduce each region to one row.

## 4. ORDER BY inside a window

```sql
SELECT
    order_id,
    order_date,
    amount,
    SUM(amount) OVER (
        ORDER BY order_date, order_id
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total
FROM orders;
```

The window ORDER BY determines the sequence used by the calculation; it does not necessarily sort the final output. Add a query-level ORDER BY if you need sorted display.

The explicit frame means “from the first row in the ordered window through the current row”. Including a unique tie-breaker such as order_id makes the sequence deterministic.

## 5. Ranking functions

```sql
SELECT
    product,
    revenue,
    ROW_NUMBER() OVER (ORDER BY revenue DESC) AS row_num,
    RANK() OVER (ORDER BY revenue DESC) AS rank_num,
    DENSE_RANK() OVER (ORDER BY revenue DESC) AS dense_rank_num
FROM product_revenue;
```

- ROW_NUMBER assigns a unique sequential number, even when values tie.
- RANK gives tied rows the same rank and leaves gaps after ties.
- DENSE_RANK gives tied rows the same rank without gaps.

For values 100, 90, 90, 80: row numbers are 1,2,3,4; ranks are 1,2,2,4; dense ranks are 1,2,2,3.

Partition ranking by category to rank products within each category.

## 6. LAG and LEAD

LAG accesses a previous row in the ordered window; LEAD accesses a following row:

```sql
SELECT
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month) AS previous_month_revenue,
    LEAD(revenue) OVER (ORDER BY month) AS next_month_revenue
FROM monthly_revenue
ORDER BY month;
```

The first row has no previous row, so LAG returns NULL unless a default is supplied. These functions are useful for month-over-month comparisons, event sequences and changes over time.

## 7. Percentage change

```sql
WITH comparisons AS (
    SELECT
        month,
        revenue,
        LAG(revenue) OVER (ORDER BY month) AS previous_revenue
    FROM monthly_revenue
)
SELECT
    month,
    revenue,
    previous_revenue,
    100.0 * (revenue - previous_revenue) / NULLIF(previous_revenue, 0)
        AS pct_change
FROM comparisons
ORDER BY month;
```

NULLIF returns NULL when the previous value is zero, avoiding division by zero. A NULL percentage for the first month or a zero baseline is more honest than inventing a percentage.

## 8. Moving averages and frames

```sql
SELECT
    month,
    revenue,
    AVG(revenue) OVER (
        ORDER BY month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS three_row_average
FROM monthly_revenue;
```

This calculates an average over the current row and up to two preceding rows. It is a three-row moving average, not necessarily a three-calendar-month average if months are missing. Ensure the dataset has a complete monthly series if you intend a true three-month measure.

## 9. Window frame awareness

Window functions can use ROWS, RANGE and (in supported engines) GROUPS frames. ROWS counts physical rows in the ordered partition. RANGE considers ordering values and peer rows. Default frames can produce surprising results, especially when ORDER BY values tie. For running totals, explicitly specify the frame and a deterministic ordering when that matches the intended definition.

## Guided exercises

1. Add the overall sales total to every order.
2. Add a regional total without reducing order rows.
3. Rank products within each category.
4. Compare RANK and DENSE_RANK with tied values.
5. Calculate monthly revenue and previous-month revenue.
6. Calculate a three-row moving average.
7. Explain why a three-row average is not always a three-month average.

## Independent practice

Create daily sales data for two regions. Calculate a running total per region, rank each day's revenue within its region, calculate day-over-day change and a seven-row moving average. Include tied values and missing dates; explain how your ordering and frame affect interpretation.

## Summary

Window functions preserve row-level detail while calculating across related rows. PARTITION BY defines groups; ORDER BY defines sequence; ranking functions order records; LAG/LEAD compare adjacent rows; frames define which rows contribute to calculations.

## Next lesson

We will combine these SQL techniques to solve realistic analytical problems such as customer segmentation, cohort retention and conditional metrics.