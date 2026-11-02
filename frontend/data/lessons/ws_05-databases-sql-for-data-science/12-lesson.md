# Lesson 12: Advanced Analytical SQL: Segmentation, Cohorts and Trends

## Purpose

This lesson combines filtering, aggregation, joins, CTEs and window functions into practical data-science questions. The goal is not to learn a new isolated command; it is to learn how to translate a business or research question into a defensible query.

## Learning outcomes

Define the grain and denominator of a metric; build customer segments; calculate repeat activity and retention; analyse time trends; use conditional aggregation; and validate analytical outputs.

## 1. Translate a question before writing SQL

Question: “Which customers are most valuable?” This is incomplete. Valuable by revenue, margin, frequency, recency or lifetime value? Over what period? Are cancelled orders excluded? Does revenue include tax or refunds? The first task is to define the metric, population, period and grain.

A useful metric specification includes:
- Entity: customer.
- Period: for example, calendar year 2026.
- Inclusion: paid/completed orders only.
- Measure: sum of net order value.
- Grain: one output row per customer.
- Missing-value rule: exclude or investigate orders with unknown amount.

## 2. Customer-level summaries

```sql
WITH customer_metrics AS (
    SELECT
        customer_id,
        COUNT(*) AS order_count,
        SUM(amount) AS total_spend,
        AVG(amount) AS average_order_value,
        MAX(order_date) AS most_recent_order
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
)
SELECT *
FROM customer_metrics
ORDER BY total_spend DESC;
```

The CTE produces one row per customer. The outer query sorts customers by total spend. Confirm that each order appears once in the source table and that refunds or returns are treated consistently.

## 3. Segment customers with CASE

```sql
WITH customer_metrics AS (
    SELECT customer_id, COUNT(*) AS order_count, SUM(amount) AS total_spend
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
)
SELECT
    customer_id,
    order_count,
    total_spend,
    CASE
        WHEN total_spend >= 500000 THEN 'High value'
        WHEN total_spend >= 100000 THEN 'Medium value'
        ELSE 'Low value'
    END AS spend_segment
FROM customer_metrics;
```

Thresholds are illustrative, not universal. In real analysis, justify them using business context, distribution quantiles or a documented policy. Do not choose thresholds after seeing the output merely to create attractive segment sizes.

## 4. Recency, frequency and monetary value

A common customer-analysis framework is RFM:
- Recency: how recently the customer purchased.
- Frequency: how often they purchased in a defined period.
- Monetary: how much they spent in that period.

SQL can calculate the three measures. SQLite date functions can calculate date differences, but date formats and timezones must be consistent. For reproducible work, pass an explicit analysis date from Python rather than relying on a changing current date.

## 5. Cohort analysis

A cohort groups entities by a shared starting event, often the month of first purchase or registration. Retention asks what proportion of the cohort returns in later periods.

The workflow:
1. Find each customer's first activity month.
2. Assign each customer to that cohort month.
3. Find each customer's active months.
4. Calculate the month offset from cohort start.
5. Count active customers by cohort and offset.
6. Divide by the cohort's starting population.

A simplified SQLite example, assuming ISO date strings and one row per event:

```sql
WITH first_activity AS (
    SELECT customer_id,
           MIN(date(activity_date, 'start of month')) AS cohort_month
    FROM activities
    GROUP BY customer_id
),
activity_months AS (
    SELECT DISTINCT customer_id,
           date(activity_date, 'start of month') AS activity_month
    FROM activities
),
cohort_activity AS (
    SELECT
        f.cohort_month,
        a.activity_month,
        CAST(strftime('%Y', a.activity_month) AS INTEGER) * 12
          + CAST(strftime('%m', a.activity_month) AS INTEGER)
          - CAST(strftime('%Y', f.cohort_month) AS INTEGER) * 12
          - CAST(strftime('%m', f.cohort_month) AS INTEGER) AS month_number,
        a.customer_id
    FROM first_activity AS f
    JOIN activity_months AS a
      ON f.customer_id = a.customer_id
)
SELECT cohort_month, month_number,
       COUNT(DISTINCT customer_id) AS active_customers
FROM cohort_activity
GROUP BY cohort_month, month_number
ORDER BY cohort_month, month_number;
```

This produces active counts, not yet retention percentages. To calculate retention, divide by the cohort's month-zero customer count. The denominator must remain the original cohort size, not the active count in the current month. A complete cohort matrix also needs a calendar of periods so that zero-activity cells are visible rather than absent.

## 6. Trend analysis

Aggregate daily or monthly metrics, then use LAG to compare periods. A missing month can make “previous row” different from “previous calendar month”. Generate or join to a complete calendar series when the business question requires every calendar period.

## 7. Conditional aggregation for analytical tables

```sql
SELECT
    region,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
    SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END) AS completed_revenue
FROM orders
GROUP BY region;
```

A grouped query can create a compact regional KPI table. Define whether cancellation rate uses all orders, submitted orders or another denominator.

## 8. Validate the output

Analytical SQL needs validation:
- Check the row grain and uniqueness of the key.
- Reconcile counts to a simpler baseline query.
- Check totals before and after joins.
- Inspect NULL and zero values.
- Test boundary dates and threshold values.
- Compare a sample of rows manually.
- Check whether the metric's denominator matches its written definition.

## Guided exercises

1. Calculate customer frequency and total spend.
2. Create three spend segments with stated thresholds.
3. Calculate monthly active customers.
4. Find each customer's first activity month.
5. Build cohort active counts and month offsets.
6. Calculate retention with a fixed cohort denominator.
7. Compare monthly revenue to the previous month.

## Independent practice

Using a synthetic transaction database, write a mini analytical report containing customer segments, monthly revenue trends and a cohort retention table. Include a short metric dictionary that defines each measure, population, period and denominator. Explain at least three validation checks you performed.

## Summary

Advanced analytical SQL is a process: define the question, define the grain, prepare data in stages, calculate measures and validate them. SQL can support segmentation, RFM-style summaries, cohort analysis and trend reporting, but the interpretation and denominator are the analyst's responsibility.

## Next lesson

We will learn how to create and modify database structures and records, while taking care not to damage data.