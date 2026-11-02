# Lesson 16: Connecting Python to SQLite

## Why this lesson matters

The rest of the course has used Python to send SQL statements to SQLite. Now we study that connection properly. A data scientist should understand where the database lives, how a connection behaves, what a cursor does, and how to organise database access in reusable Python code.

## Learning outcomes

Explain the Python DB-API idea; open and close SQLite connections; use cursors and connection.execute; manage transactions and context managers; configure foreign keys; inspect database metadata; and organise a small Python project around a database file.

## 1. The database workflow

```text
Python application
      |
      | sqlite3.connect(...)
      v
Connection to SQLite database file
      |
      | execute(SQL, parameters)
      v
SQLite engine parses, plans and executes SQL
      |
      v
Rows / affected-row information
      |
      v
Python objects -> validation / Pandas / charts / models
```

Python does not translate SQL into Pandas. It sends SQL to the database engine. SQLite evaluates the query and returns results through the Python interface.

## 2. The sqlite3 module

`sqlite3` is included in the Python standard library. Import it with:

```python
import sqlite3
```

Check the SQLite library version linked to your Python interpreter:

```python
print(sqlite3.sqlite_version)
```

This is useful because SQLite features vary by version. For example, RIGHT and FULL OUTER JOIN support requires SQLite 3.39.0 or later.

## 3. Opening a connection

```python
connection = sqlite3.connect("data/learning.db")
```

If the file exists, SQLite opens it. If it does not exist, SQLite normally creates a new database file. A typo in the path can therefore create an unintended empty database rather than reporting that the intended file is missing. For important workflows, verify the path and existence before connecting.

For a read-only connection, SQLite supports a URI form:

```python
connection = sqlite3.connect(
    "file:data/learning.db?mode=ro",
    uri=True
)
```

This prevents accidental writes through that connection. The file must already exist. URI options should be used deliberately and with correctly formed paths.

## 4. Connection and cursor

A connection represents the database session and transaction boundary. A cursor is an interface for executing statements and retrieving result rows. Python's sqlite3 also allows executing SQL directly on the connection:

```python
with sqlite3.connect("data/learning.db") as connection:
    rows = connection.execute(
        "SELECT student_id, name FROM students"
    ).fetchall()
```

This is concise for many scripts. Explicit cursors are still useful when you need to manage repeated fetch operations or understand the DB-API pattern:

```python
connection = sqlite3.connect("data/learning.db")
cursor = connection.cursor()
cursor.execute("SELECT name FROM students")
row = cursor.fetchone()
cursor.close()
connection.close()
```

## 5. Context managers and closing

The connection context manager commits an open transaction on successful exit and rolls it back if an exception occurs. It does **not** close the connection. Close explicitly, or use try/finally:

```python
connection = sqlite3.connect("data/learning.db")
try:
    rows = connection.execute("SELECT COUNT(*) FROM students").fetchone()
finally:
    connection.close()
```

For short scripts, a clear pattern is:

```python
with sqlite3.connect("data/learning.db") as connection:
    connection.execute("PRAGMA foreign_keys = ON")
    rows = connection.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()
```

For a long-lived connection, manage its lifecycle explicitly.

## 6. Row factories

By default, rows are tuples. You can set `row_factory` to access columns by name:

```python
import sqlite3

connection = sqlite3.connect("data/learning.db")
connection.row_factory = sqlite3.Row

try:
    rows = connection.execute(
        "SELECT student_id, name FROM students"
    ).fetchall()
    for row in rows:
        print(row["student_id"], row["name"])
finally:
    connection.close()
```

Named access can make code clearer, especially when queries return many columns. It does not turn the results into a Pandas DataFrame.

## 7. Inspect tables and schema

SQLite stores schema information in `sqlite_schema`:

```python
with sqlite3.connect("data/learning.db") as connection:
    tables = connection.execute("""
        SELECT name, sql
        FROM sqlite_schema
        WHERE type = 'table'
        ORDER BY name
    """).fetchall()
```

To inspect columns of a particular table:

```python
with sqlite3.connect("data/learning.db") as connection:
    columns = connection.execute(
        "PRAGMA table_info(students)"
    ).fetchall()
```

The table name in a PRAGMA statement is part of SQL syntax, not a bound value placeholder. If table names are dynamic, validate them against an allow-list rather than interpolating arbitrary input.

## 8. Enable foreign keys

SQLite foreign-key enforcement must be enabled for each connection:

```python
def open_database(path="data/learning.db"):
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection
```

Use this helper consistently. If you enable foreign keys after beginning a transaction, the setting may not take effect as expected; configure it immediately after connecting.

## 9. A reusable project structure

```text
sql_data_science/
├── data/
│   └── learning.db
├── src/
│   ├── database.py
│   └── analysis.py
├── scripts/
│   └── create_database.py
└── requirements.txt
```

For the built-in sqlite3 module, no package requirement is needed. Later, Pandas will be installed in the selected Python environment. Keep database connection logic in one module rather than copying slightly different connection code throughout the project.

## Guided exercises

1. Print the SQLite version.
2. Open the learning database and count students.
3. Retrieve a row using tuple access and then using sqlite3.Row.
4. List all tables from sqlite_schema.
5. Inspect the columns of enrolments.
6. Write an open_database function that enables foreign keys.
7. Demonstrate that a read-only connection rejects a write.

## Independent practice

Create a Python module that exposes a function to open the course database and a function that returns a list of table names. Add error handling for a missing or invalid path. Explain why the connection context manager and connection.close() are different responsibilities.

## Summary

Python's sqlite3 module is the interface between Python and SQLite. A connection manages the database session and transactions; cursors execute statements and fetch rows. Use context managers, explicit connection lifecycle management, row factories where useful and foreign-key enforcement on each connection.

## Next lesson

We will use the connection to execute parameterised SQL, handle results and errors, and perform safe data changes from Python.