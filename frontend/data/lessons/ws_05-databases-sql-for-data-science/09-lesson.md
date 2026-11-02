# Lesson 09: Set Operations and Combining Query Results

## Learning outcomes

Distinguish horizontal combination through joins from vertical combination through set operations; use UNION and UNION ALL; understand INTERSECT and EXCEPT; align columns correctly; and identify duplicate-handling consequences.

## 1. Two different ways to combine data

A JOIN combines columns from related rows. A set operation stacks or compares rows from two query results. Think of two lists of students: UNION can combine the lists into one result, while a JOIN might attach each student's department or enrolment information.

## 2. UNION

`UNION` combines result rows and removes duplicate rows:

```sql
SELECT email FROM current_students
UNION
SELECT email FROM former_students;
```

The two SELECT statements must return the same number of columns, in compatible positions and with compatible types. The output column names are generally taken from the first SELECT.

UNION removes duplicate result rows across the combined output. That deduplication has a cost, so do not use it automatically when duplicates are meaningful.

## 3. UNION ALL

`UNION ALL` appends all rows and preserves duplicates:

```sql
SELECT email FROM current_students
UNION ALL
SELECT email FROM former_students;
```

Use it when every row represents a meaningful observation or when you know the inputs do not overlap. It is generally more efficient than UNION because it does not need to eliminate duplicates.

A duplicate is not automatically an error. If the same customer appears in two monthly transaction extracts, those may be two legitimate transactions. The correct choice depends on the grain and meaning of the data.

## 4. Aligning columns

This is valid:

```sql
SELECT student_id, name FROM cohort_a
UNION ALL
SELECT student_id, name FROM cohort_b;
```

This is not a sensible alignment:

```sql
SELECT student_id, name FROM cohort_a
UNION ALL
SELECT name, student_id FROM cohort_b;
```

The database aligns by position, not by the meaning of the column names. The second query can place names in an ID output column. Explicitly select columns in the same semantic order and cast types when necessary.

## 5. INTERSECT

`INTERSECT` returns distinct rows present in both result sets:

```sql
SELECT student_id FROM cohort_a
INTERSECT
SELECT student_id FROM scholarship_recipients;
```

This finds IDs common to both groups. It is useful for overlap analysis, but it removes duplicates. If repeated observations matter, use a different approach.

## 6. EXCEPT

`EXCEPT` returns distinct rows in the first result that are not present in the second:

```sql
SELECT student_id FROM registered_students
EXCEPT
SELECT student_id FROM completed_students;
```

This finds registered students not represented in the completed set. Direction matters: A EXCEPT B is not the same as B EXCEPT A.

SQLite supports UNION, UNION ALL, INTERSECT and EXCEPT. Parentheses and ORDER BY placement can vary among SQL dialects; in SQLite, ORDER BY applies to the compound result and should normally appear at the end.

## 7. Combining query results in Python

```python
import sqlite3

sql = """
SELECT student_id, name, 'current' AS cohort
FROM current_students
UNION ALL
SELECT student_id, name, 'former' AS cohort
FROM former_students
ORDER BY name;
"""

with sqlite3.connect("data/learning.db") as connection:
    rows = connection.execute(sql).fetchall()

for row in rows:
    print(row)
```

The literal label creates a column identifying the source group. This is often useful when combining data from multiple periods or sources.

## 8. When set operations are not the right tool

If you need to add a customer's city to their order rows, use a JOIN. If you need to append January transactions to February transactions, use UNION ALL. If you need to identify records shared between two lists, INTERSECT may help. If you need records present in one list but absent from another, EXCEPT or an anti-join may help.

## Guided exercises

1. Combine two cohort tables with UNION ALL.
2. Repeat with UNION and compare row counts.
3. Find IDs present in both a training and scholarship table using INTERSECT.
4. Find students in one table but not another using EXCEPT.
5. Add a source label to each SELECT before combining.
6. Explain why columns must be selected in the same order.

## Independent practice

Create two tables containing monthly sales records. Include some repeated customers and a transaction that appears in both extracts. Combine the data using UNION ALL, then investigate whether UNION would incorrectly remove a legitimate repeated transaction. Write an overlap query using INTERSECT and explain the meaning of the result.

## Summary

Set operations combine compatible query results vertically. UNION removes duplicate rows; UNION ALL preserves them; INTERSECT finds shared rows; EXCEPT finds rows in the first result absent from the second. Choose based on the meaning of a record, not merely on whether duplicates look untidy.

## Next lesson

As analytical questions become more complex, queries can become difficult to read. Subqueries and common table expressions let us break a large question into understandable steps.