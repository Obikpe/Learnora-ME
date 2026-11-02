# Lesson 05: Sorting, Limiting and Transforming Results

## Learning outcomes

Sort query results using `ORDER BY`, use multiple sort keys, limit result size, understand ties, create conditional categories with `CASE`, and apply common text, numeric and date functions in SQLite.

## 1. Why sorting is explicit

A database table is a logical collection of rows, not a promise that records will appear in insertion order. If you need a predictable order, request it:

```sql
SELECT name, age
FROM students
ORDER BY age;
```

Ascending order is the default. Use `ASC` to make it explicit or `DESC` for descending order:

```sql
SELECT name, age
FROM students
ORDER BY age DESC;
```

Sorting is applied to the result rows. It does not permanently rearrange the stored table.

## 2. Sort using more than one column

```sql
SELECT programme, name, age
FROM students
ORDER BY programme ASC, age DESC, name ASC;
```

SQLite sorts first by programme. Where programmes are equal, it sorts by age descending. Where both are equal, it sorts by name ascending. Later keys break ties left by earlier keys.

A stable final tie-breaker such as a unique ID is useful when you need repeatable ordering:

```sql
ORDER BY age DESC, student_id ASC;
```

## 3. LIMIT

`LIMIT` restricts the number of returned rows:

```sql
SELECT name, age
FROM students
ORDER BY age DESC
LIMIT 3;
```

Always pair a limit with an intentional sort when you mean “top three”. Without `ORDER BY`, the selected three rows are not a meaningful ranking.

SQLite also supports `LIMIT n OFFSET m` for simple pagination:

```sql
SELECT student_id, name
FROM students
ORDER BY student_id
LIMIT 10 OFFSET 20;
```

This skips 20 rows and returns up to 10. Large offsets can become inefficient in some systems; keyset pagination is often better for large changing datasets.

## 4. CASE expressions

`CASE` creates a conditional result:

```sql
SELECT
    name,
    age,
    CASE
        WHEN age < 22 THEN 'Younger'
        WHEN age <= 24 THEN 'Middle'
        ELSE 'Older'
    END AS age_group
FROM students;
```

The database checks WHEN conditions in order and returns the result for the first true condition. If none matches, ELSE is used. If ELSE is omitted and no condition matches, the result is NULL.

The order matters: the first matching condition wins. CASE is useful for grouping values into categories, creating flags and translating coded values into readable labels.

## 5. Text functions

SQLite provides functions such as:
- `LOWER(text)`: converts text to lowercase for supported characters.
- `UPPER(text)`: converts text to uppercase.
- `LENGTH(text)`: returns text length.
- `TRIM(text)`: removes leading and trailing spaces.
- `SUBSTR(text, start, length)`: extracts part of a string.
- `REPLACE(text, old, new)`: replaces matching text.

Example:

```sql
SELECT
    name,
    UPPER(name) AS name_upper,
    LENGTH(name) AS name_length
FROM students;
```

These expressions transform the returned value; they do not update the stored name. Cleaning stored data is a separate operation and should be done deliberately.

## 6. Numeric functions and arithmetic

Arithmetic operators include `+`, `-`, `*` and `/`. SQLite also provides functions such as `ROUND(value, digits)`, `ABS(value)` and `MAX`/`MIN` in their scalar or aggregate contexts.

```sql
SELECT
    amount,
    ROUND(amount * 1.075, 2) AS amount_with_tax
FROM orders;
```

Understand the units and assumptions behind a calculation. Rounding for display is not always the same as rounding values before aggregation. If financial precision matters, consider integer minor units (such as kobo or cents) or an engine with an appropriate exact decimal type.

## 7. Dates and times in SQLite

SQLite does not have a dedicated date/time storage type in the same way some database systems do. Dates and times are commonly stored as ISO-8601 text, Unix timestamps or Julian day values. Consistent ISO-8601 text such as `2026-03-15` sorts chronologically when formatted consistently.

SQLite date/time functions include `date()`, `time()`, `datetime()`, `strftime()` and `julianday()`. Example:

```sql
SELECT
    order_date,
    strftime('%Y', order_date) AS order_year,
    strftime('%m', order_date) AS order_month
FROM orders;
```

The format codes are important: `%Y` is a four-digit year and `%m` is a two-digit month. Date parsing and timezone handling require care. Store timestamps consistently, define the timezone convention, and do not assume a date-only value contains a time or timezone.

## 8. Combining transformation and filtering

A query can filter, calculate and sort:

```sql
SELECT
    name,
    age,
    CASE
        WHEN age < 22 THEN 'Under 22'
        ELSE '22 or older'
    END AS age_band
FROM students
WHERE age IS NOT NULL
ORDER BY age DESC, name ASC
LIMIT 5;
```

Read the query by its clauses. Conceptually, SQL processes filtering before final projection and ordering, although the query optimiser chooses the physical execution plan. You will learn a more precise logical processing model in later lessons.

## Guided practice

1. Sort students from oldest to youngest.
2. Sort by programme and then name.
3. Return the two oldest students with a unique ID as a tie-breaker.
4. Create a CASE expression that labels ages as `Under 22`, `22–24` or `25+`.
5. Convert student names to uppercase in the output.
6. For an orders table, extract year and month from an ISO date.

## Independent practice

Build a product table with price, category and product name. Write queries to calculate a 10% price increase, round the displayed result, label price bands with CASE, sort products by category and descending price, and return the five most expensive products. Explain why LIMIT without a deterministic ORDER BY can be misleading.

## Lesson summary

Sorting is controlled by `ORDER BY`; `LIMIT` controls result size; multiple sort keys resolve ties; `CASE` creates conditional labels; and built-in functions transform text, numbers and dates. These operations make raw query results more useful for analysis.

## Next lesson

We will move from individual records to summaries: counts, totals, averages and grouped comparisons using aggregate functions, GROUP BY and HAVING.