# Lesson 17: Executing SQL Safely from Python

## Learning outcomes

Execute SELECT and write statements; bind parameters safely; use executemany; retrieve rows; understand rowcount and lastrowid; manage transactions; handle database errors; and avoid SQL injection.

## 1. Execute a query

```python
import sqlite3

with sqlite3.connect("data/learning.db") as connection:
    cursor = connection.execute(
        "SELECT student_id, name FROM students"
    )
    rows = cursor.fetchall()

print(rows)
```

The SQL statement is sent to SQLite. The returned cursor provides the result rows. SELECT does not normally change stored data.

## 2. Parameterised queries

Never insert user-provided values into SQL with string concatenation or f-strings:

```python
# Unsafe: do not do this
name = input("Student name: ")
sql = f"SELECT * FROM students WHERE name = '{name}'"
```

If input contains quotes or SQL syntax, the constructed statement may behave differently from what you intended. This is the core idea behind SQL injection.

Use placeholders and pass values separately:

```python
name = input("Student name: ")

with sqlite3.connect("data/learning.db") as connection:
    rows = connection.execute(
        "SELECT student_id, name FROM students WHERE name = ?",
        (name,)
    ).fetchall()
```

The database treats the supplied value as data, not executable SQL. In sqlite3, qmark placeholders use `?`; named placeholders use forms such as `:name`.

```python
with sqlite3.connect("data/learning.db") as connection:
    rows = connection.execute(
        "SELECT student_id, name FROM students WHERE programme = :programme",
        {"programme": "Data Science"}
    ).fetchall()
```

Use the placeholder style consistently. Do not quote the placeholder yourself.

## 3. Parameters are for values, not identifiers

A placeholder can represent a value, not a table or column name. This does not work as intended:

```python
# A placeholder cannot stand for a column identifier
connection.execute("SELECT ? FROM students", ("name",))
```

If a user can choose a sort column, map their choice to a fixed allow-list:

```python
allowed_sort_columns = {
    "name": "name",
    "age": "age",
    "programme": "programme",
}

requested = "age"
column = allowed_sort_columns[requested]

sql = f"SELECT student_id, name, age FROM students ORDER BY {column}"
```

This interpolation is acceptable only because `column` comes from a fixed trusted mapping, not raw user input. The values in WHERE still use placeholders.

## 4. Insert one record

```python
student = ("Zara", "Data Science", 23)

with sqlite3.connect("data/learning.db") as connection:
    cursor = connection.execute("""
        INSERT INTO students (name, programme, age)
        VALUES (?, ?, ?)
    """, student)
    new_id = cursor.lastrowid

print("New student ID:", new_id)
```

lastrowid reports the row ID from the most recent relevant INSERT on that cursor. It is not a universal identifier for every kind of insert, and it should be read immediately after the insert whose ID you need.

## 5. Insert many records with executemany

```python
new_students = [
    ("Ife", "Statistics", 26),
    ("Noah", "Data Science", 22),
    ("Lara", "Business Analytics", 24),
]

with sqlite3.connect("data/learning.db") as connection:
    connection.executemany("""
        INSERT INTO students (name, programme, age)
        VALUES (?, ?, ?)
    """, new_students)
```

executemany executes the parameterised statement for each parameter set. It is convenient for bulk inserts. For very large ingestion workloads, consider batching, transactions and memory use.

## 6. Update and delete

```python
student_id = 3
new_age = 22

with sqlite3.connect("data/learning.db") as connection:
    cursor = connection.execute(
        "UPDATE students SET age = ? WHERE student_id = ?",
        (new_age, student_id)
    )
    print("Rows affected:", cursor.rowcount)
```

For DELETE, use the same pattern and a carefully chosen WHERE condition. A rowcount of zero may mean the ID did not exist or the update did not change any rows, depending on the driver/database semantics. Verify the final state with SELECT.

## 7. Transactions and rollback

```python
import sqlite3

connection = sqlite3.connect("data/learning.db")
try:
    connection.execute("BEGIN")
    connection.execute(
        "UPDATE products SET price = ? WHERE product_id = ?",
        (2000, 1)
    )
    connection.execute(
        "INSERT INTO audit_log(action) VALUES (?)",
        ("product price updated",)
    )
    connection.commit()
except sqlite3.Error:
    connection.rollback()
    raise
finally:
    connection.close()
```

All related operations succeed together or are rolled back. Ensure every table and column used in the example exists in your database before running it.

## 8. Handle exceptions thoughtfully

Common exception types include:
- `sqlite3.IntegrityError`: a constraint was violated.
- `sqlite3.OperationalError`: a database operation could not be completed, such as a missing table or locked database.
- `sqlite3.ProgrammingError`: incorrect API usage, such as parameter mismatch.
- `sqlite3.DatabaseError`: broader database-related failure.

Catch the narrowest useful exception. Do not hide errors with a blanket `except: pass`. Log enough context to diagnose the issue, but do not log passwords, sensitive personal data or raw secrets.

## 9. Validate input before writing

Parameterisation protects the SQL statement; it does not prove the value makes business sense. Validate that age is a plausible non-negative integer, amount is within expected bounds and required text is not blank. Database constraints provide a second line of defence.

## Guided exercises

1. Query students by programme using a parameter.
2. Query by a named placeholder.
3. Insert a student and retrieve lastrowid.
4. Insert five records with executemany.
5. Update a record and inspect rowcount.
6. Attempt a duplicate unique value and handle IntegrityError.
7. Explain why parameter placeholders cannot be used for table names.

## Independent practice

Write a small Python CRUD module for a `products` table. Include create, read, update and delete functions. All values must be parameterised; update/delete must require a product ID; functions should return useful results; invalid input and integrity errors should be handled without silently suppressing them. Add a test script that verifies each operation.

## Summary

Python sends SQL through execute and executemany. Bind all external values with placeholders. Use allow-lists for dynamic identifiers. Manage transactions explicitly, inspect affected rows and handle expected database errors. Parameterisation prevents SQL injection through values, while validation protects business rules.

## Next lesson

We will combine SQL and Pandas: query a database into DataFrames, write DataFrames to SQLite and decide which work belongs in SQL versus Python.