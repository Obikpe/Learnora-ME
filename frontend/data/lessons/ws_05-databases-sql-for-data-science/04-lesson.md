# Lesson 04: Filtering Data with WHERE

## Why filtering matters

A database may contain millions of records, while your analysis may concern one region, a date range or a particular customer group. Filtering tells the database which rows should appear in the result. A correct filter is essential: a small logical mistake can produce a misleading analysis.

## Learning outcomes

Use comparison operators, combine conditions with `AND` and `OR`, negate conditions with `NOT`, filter sets and ranges with `IN` and `BETWEEN`, match text with `LIKE`, and handle missing values with `IS NULL`.

## 1. Start with one condition

```sql
SELECT name, age
FROM students
WHERE age >= 23;
```

The database examines each row and keeps rows for which the condition is true. The comparison operators are:
- `=` equal to
- `!=` or `<>` not equal to
- `>` greater than
- `<` less than
- `>=` greater than or equal to
- `<=` less than or equal to

Text values are written in single quotes in SQL:

```sql
SELECT *
FROM students
WHERE programme = 'Data Science';
```

SQL string comparisons depend on the database's collation and comparison rules. Do not assume every database treats letter case identically.

## 2. AND and OR

`AND` requires both conditions to be true:

```sql
SELECT name, programme, age
FROM students
WHERE programme = 'Data Science'
  AND age >= 22;
```

`OR` requires at least one condition to be true:

```sql
SELECT name, programme
FROM students
WHERE programme = 'Data Science'
   OR programme = 'Statistics';
```

When combining them, use parentheses to make the intended logic explicit:

```sql
SELECT *
FROM students
WHERE (programme = 'Data Science' OR programme = 'Statistics')
  AND age >= 22;
```

Without parentheses, SQL applies operator precedence rules. Parentheses make complex conditions easier to inspect and reduce accidental logic errors.

## 3. NOT

`NOT` reverses a condition:

```sql
SELECT *
FROM students
WHERE NOT programme = 'Statistics';
```

This returns rows for which the comparison is not true. Be careful with `NULL`: SQL uses three-valued logic (true, false and unknown), so negating a condition involving a missing value does not necessarily include that row.

## 4. IN for a list of allowed values

Instead of writing several OR conditions:

```sql
SELECT *
FROM students
WHERE programme IN ('Data Science', 'Statistics');
```

This is easier to read when checking membership in a known list. `NOT IN` excludes listed values, but a list containing `NULL` can produce surprising unknown results. Prefer a carefully understood list and handle missing values explicitly.

## 5. BETWEEN for a range

```sql
SELECT *
FROM students
WHERE age BETWEEN 21 AND 24;
```

`BETWEEN` includes both endpoints. This is equivalent to `age >= 21 AND age <= 24`. For timestamps, inclusive endpoints can be tricky; a half-open interval (start inclusive, next boundary exclusive) is often safer for date/time analysis.

## 6. LIKE for text patterns

SQLite uses `LIKE` for simple pattern matching:
- `'A%'`: begins with A.
- `'%a'`: ends with a.
- `'%at%'`: contains at.
- `'_da'`: any one character followed by da.

```sql
SELECT *
FROM students
WHERE name LIKE 'A%';
```

The percent sign matches zero or more characters. The underscore matches exactly one character. Case sensitivity for ASCII characters in SQLite's default `LIKE` behaviour differs from some other engines and can be configured; do not assume identical behaviour across every SQL system.

## 7. NULL is not an ordinary value

A missing value is represented by `NULL`. It does not mean zero, an empty string or the word "NULL". Because a missing value is unknown, this is incorrect:

```sql
-- Incorrect way to test for missing values
WHERE age = NULL
```

Use:

```sql
SELECT *
FROM students
WHERE age IS NULL;
```

To find present values:

```sql
SELECT *
FROM students
WHERE age IS NOT NULL;
```

A comparison such as `age = 25` evaluates to unknown when age is NULL. The WHERE clause keeps only rows for which its condition is true.

## 8. Filtering from Python safely

You can send a filter through Python. If the value comes from a variable or user input, use placeholders:

```python
import sqlite3

programme = "Data Science"

with sqlite3.connect("data/learning.db") as connection:
    rows = connection.execute(
        """
        SELECT name, age
        FROM students
        WHERE programme = ?
        """,
        (programme,)
    ).fetchall()

print(rows)
```

The comma in `(programme,)` matters: it creates a one-item tuple. Values are passed separately from SQL text. This is called parameter binding and helps prevent SQL injection. Do not build a query by inserting untrusted text with f-strings or string concatenation.

## 9. A systematic way to debug a filter

When a result looks wrong:
1. Run the query without the WHERE clause and inspect the underlying values.
2. Test one condition at a time.
3. Check spelling, spaces, data types and missing values.
4. Add combined conditions gradually.
5. Count the returned rows and compare with what you expect.
6. Check whether parentheses express the intended logic.

## Guided exercises

Using the students table:
1. Find students aged below 24.
2. Find students in Statistics or Business Analytics.
3. Find Data Science students aged at least 22.
4. Find names beginning with K.
5. Find rows with a missing age (first insert a test row with NULL if necessary).
6. Rewrite an `IN` query using OR and compare the results.

## Independent practice

Run `python scripts/seed_course_data.py` once if you have not already done so. Use the seeded `orders` table (eight sample orders across four regions and four customers). Write at least eight filtering queries, including a date range, a region, a status, a minimum amount and a combined condition. For each query, explain in plain language exactly why each returned row qualifies. Add one new order with a missing optional amount only after checking the table schema and constraints.

## Lesson summary

`WHERE` filters rows. Comparisons, logical operators, `IN`, `BETWEEN` and `LIKE` cover common conditions. Missing values require `IS NULL` or `IS NOT NULL`; ordinary equality does not work for NULL. In Python, pass values using placeholders rather than inserting them into SQL strings.

## Next lesson

After selecting the correct rows, analysts often need them in a meaningful order, a manageable number of records or a transformed form. We will use sorting, limits and common SQL functions.