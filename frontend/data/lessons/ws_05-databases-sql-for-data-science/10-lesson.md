# Lesson 10: Subqueries and Common Table Expressions (CTEs)

## Learning outcomes

Write scalar, multi-row and correlated subqueries; use IN and EXISTS; understand subquery scope; build CTEs with WITH; chain multiple CTEs; and choose a readable approach for multi-step analysis.

## 1. What is a subquery?

A subquery is a query nested inside another SQL statement. The inner query produces a value or result set that the outer query uses. Subqueries let you express a question in stages.

Suppose you want orders larger than the average order amount:

```sql
SELECT order_id, amount
FROM orders
WHERE amount > (
    SELECT AVG(amount)
    FROM orders
);
```

The inner query calculates one value: the average amount. The outer query compares each order against that value. This is a scalar subquery because it returns one value.

## 2. Subqueries with IN

Find students enrolled in a particular course:

```sql
SELECT student_id, name
FROM students
WHERE student_id IN (
    SELECT student_id
    FROM enrolments
    WHERE course_id = 2
);
```

The inner query returns a set of student IDs. IN checks whether each outer student ID belongs to that set.

## 3. EXISTS

EXISTS tests whether a subquery returns at least one row:

```sql
SELECT s.student_id, s.name
FROM students AS s
WHERE EXISTS (
    SELECT 1
    FROM enrolments AS e
    WHERE e.student_id = s.student_id
);
```

The inner query is correlated because it refers to `s.student_id` from the outer query. Conceptually, the database checks whether a matching enrolment exists for each student. The SELECT 1 is conventional: EXISTS cares about row existence, not the selected value.

NOT EXISTS finds rows with no match:

```sql
SELECT s.student_id, s.name
FROM students AS s
WHERE NOT EXISTS (
    SELECT 1
    FROM enrolments AS e
    WHERE e.student_id = s.student_id
);
```

This is often safer than NOT IN when the subquery might contain NULL.

## 4. Correlated subqueries

A correlated subquery depends on values from the outer query. Example: find each order whose amount is above the average for its own region.

```sql
SELECT o.order_id, o.region, o.amount
FROM orders AS o
WHERE o.amount > (
    SELECT AVG(other.amount)
    FROM orders AS other
    WHERE other.region = o.region
);
```

The inner average is restricted to the current row's region. This is powerful but can be harder to read and may be more expensive depending on the optimiser and indexes. A grouped CTE or window function may express the same task more clearly.

## 5. A subquery in FROM

A subquery can create a derived table:

```sql
SELECT regional.region, regional.revenue
FROM (
    SELECT region, SUM(amount) AS revenue
    FROM orders
    GROUP BY region
) AS regional
WHERE regional.revenue > 100000;
```

The inner query creates a temporary result with one row per region. The outer query filters that result. The alias `regional` is required in many SQL dialects and is good practice.

## 6. Common Table Expressions

A CTE names a query result for use by the statement that follows:

```sql
WITH regional_revenue AS (
    SELECT region, SUM(amount) AS revenue
    FROM orders
    GROUP BY region
)
SELECT region, revenue
FROM regional_revenue
WHERE revenue > 100000;
```

The WITH clause makes the stages visible. A CTE is not automatically a permanent table; its scope is the single SQL statement. Depending on the engine and query, it may be inlined or materialised. Do not assume a CTE is always faster than a subquery.

## 7. Multiple CTEs

```sql
WITH
monthly_sales AS (
    SELECT
        strftime('%Y-%m', order_date) AS month,
        SUM(amount) AS revenue
    FROM orders
    GROUP BY strftime('%Y-%m', order_date)
),
ranked_months AS (
    SELECT
        month,
        revenue,
        RANK() OVER (ORDER BY revenue DESC) AS revenue_rank
    FROM monthly_sales
)
SELECT month, revenue, revenue_rank
FROM ranked_months
ORDER BY revenue_rank, month;
```

Each CTE can build on the previous one. This query first summarises monthly sales, then ranks the summaries, then returns the ranked result. Window functions are introduced in Lesson 11; this example previews the idea.

## 8. Choosing between subqueries, joins and CTEs

- Use a JOIN when you need columns from related rows.
- Use EXISTS when you only need to know whether a related record exists.
- Use a scalar subquery when one calculated value is needed.
- Use a CTE when naming intermediate steps makes a multi-stage query easier to understand.
- Use a derived table when a local intermediate result is needed in FROM.

There is rarely one universally fastest form. Measure performance with representative data and inspect query plans when necessary.

## 9. Debugging multi-step SQL

Build the inner query first and run it alone. Confirm its row count, columns and values. Then place it inside the outer query. For CTEs, temporarily select from each CTE to inspect its output. Give each stage a descriptive name and keep each stage focused on one transformation.

## Guided exercises

1. Find orders above the overall average.
2. Find students enrolled in course ID 2 using IN.
3. Find students with at least one enrolment using EXISTS.
4. Find students with no enrolments using NOT EXISTS.
5. Calculate regional revenue in a CTE and filter regions above a threshold.
6. Build two CTEs: monthly revenue and a final filtered report.

## Independent practice

Using a sales database, produce a report of products whose total sales exceed the average product total. Solve it once with a subquery and once with a CTE. Explain each intermediate result, then compare readability. If you use EXISTS or NOT EXISTS, test the query with a NULL in the relevant column and explain why the result is safe.

## Summary

Subqueries let one query use another query's result. EXISTS checks for row existence; correlated subqueries refer to the outer query. CTEs name intermediate steps and make complex analysis easier to reason about. Readability and correct result grain should guide the choice.

## Next lesson

We now move into advanced analytical SQL: window functions that calculate rankings, running totals and comparisons without collapsing rows into groups.