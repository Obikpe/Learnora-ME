# Lesson 08: Joining Related Tables

## Learning outcomes

Explain why joins are needed; join tables using matching keys; distinguish INNER, LEFT, RIGHT, FULL OUTER, CROSS and self joins; diagnose duplicate rows; handle unmatched records; and validate join results.

## 1. Why join?

Student names are stored in `students`, course titles in `courses`, and registrations in `enrolments`. A report asking “Which student enrolled in which course?” needs information from all three tables. A JOIN combines related rows into a query result without permanently merging the underlying tables.

## 2. INNER JOIN

```sql
SELECT s.name, c.course_title, e.enrolled_on
FROM enrolments AS e
INNER JOIN students AS s
    ON e.student_id = s.student_id
INNER JOIN courses AS c
    ON e.course_id = c.course_id;
```

Only enrolment rows with matching student and course records appear. Table aliases (`e`, `s`, `c`) shorten references. The ON clause states how records match. Qualify columns with aliases when names may be ambiguous.

## 3. LEFT JOIN

A LEFT JOIN preserves every row from the left table, adding matching right-side values where available:

```sql
SELECT s.student_id, s.name, e.course_id
FROM students AS s
LEFT JOIN enrolments AS e
    ON s.student_id = e.student_id;
```

Students with no enrolment still appear; their enrolment columns are NULL. This is useful for finding learners who have not registered.

```sql
SELECT s.student_id, s.name
FROM students AS s
LEFT JOIN enrolments AS e
    ON s.student_id = e.student_id
WHERE e.enrolment_id IS NULL;
```

This is an anti-join pattern: return left-side records with no match.

## 4. RIGHT and FULL OUTER JOIN

RIGHT JOIN preserves all rows from the right table. FULL OUTER JOIN preserves unmatched rows from both sides. SQLite added RIGHT and FULL OUTER JOIN support in version 3.39.0. Older SQLite versions do not support them. For compatibility, a RIGHT JOIN can often be rewritten by swapping table order in a LEFT JOIN. A FULL OUTER JOIN can be emulated with a LEFT JOIN plus an anti-join from the other side combined using UNION ALL.

Do not assume every SQL dialect or installed SQLite version supports every join type. Check the engine version when needed:

```python
import sqlite3
print(sqlite3.sqlite_version)
```

## 5. CROSS JOIN

A CROSS JOIN produces every possible pair of rows from two inputs. If one table has 3 rows and another has 4, the result has 12 rows. This is a Cartesian product. It is useful for generating combinations, such as every date paired with every product, but accidental cross joins can create enormous results.

## 6. Self join

A table can be joined to itself. Suppose employees have an `employee_id` and `manager_id` that refers to another employee:

```sql
SELECT
    employee.name AS employee_name,
    manager.name AS manager_name
FROM employees AS employee
LEFT JOIN employees AS manager
    ON employee.manager_id = manager.employee_id;
```

The two aliases represent two roles played by the same table. LEFT JOIN keeps employees who have no manager.

## 7. The most important join danger: row multiplication

Suppose one customer has three orders. Joining customers to orders returns three rows for that customer. This is correct: the relationship is one-to-many. But if you later sum a customer-level value after joining, you may count it three times.

Before writing a join, state the expected grain of each table:
- customers: one row per customer.
- orders: one row per order.
- order_items: one row per product line within an order.

A join can change the grain of the result. Always ask: “What does one output row represent?”

## 8. Join keys and NULLs

Rows match when the ON condition evaluates to true. NULL does not equal NULL in ordinary equality comparisons. If a key is missing, the row may not match. Do not replace missing IDs with arbitrary values just to force a join.

## 9. Join filtering: ON versus WHERE

With an outer join, a condition on the right table in WHERE can remove unmatched rows and make the result behave like an inner join:

```sql
-- Keeps all students; only matching completed enrolments are attached
SELECT s.name, e.status
FROM students AS s
LEFT JOIN enrolments AS e
  ON s.student_id = e.student_id
 AND e.status = 'completed';
```

Compare with:

```sql
-- Removes rows where e.status is NULL; unmatched students disappear
SELECT s.name, e.status
FROM students AS s
LEFT JOIN enrolments AS e
  ON s.student_id = e.student_id
WHERE e.status = 'completed';
```

This distinction is essential when preserving unmatched records.

## 10. Validate a join

Useful checks:
- Count rows before and after the join.
- Count distinct primary keys.
- Check whether a supposed one-to-one join unexpectedly multiplies rows.
- Inspect unmatched keys with anti-join queries.
- Compare aggregate totals before and after joining.
- Confirm that the join columns represent the same entity and compatible data.

## Guided exercises

1. Join enrolments to students to display student names.
2. Join enrolments to courses to display course titles.
3. Join all three tables.
4. Find students with no enrolment.
5. Find courses with no enrolment.
6. Use a self join to show employees and managers.
7. Explain why joining orders to order_items increases row count.

## Independent practice

Create customers and orders tables. Include customers with zero, one and multiple orders. Write an inner join, left join, anti-join and grouped revenue report. Explain the grain of every result and verify that revenue is not duplicated by an additional join.

## Summary

JOIN combines related rows at query time. INNER keeps matches; LEFT preserves the left side; RIGHT and FULL OUTER preserve additional unmatched rows where supported; CROSS forms every pair; self joins give a table multiple roles. Understanding table grain and row multiplication is more important than memorising join syntax.

## Next lesson

Joins combine columns from related rows. Set operations combine result sets vertically. We will compare UNION, UNION ALL, INTERSECT and EXCEPT.