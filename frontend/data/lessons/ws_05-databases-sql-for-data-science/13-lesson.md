# Lesson 13: Creating Tables and Safely Changing Data

## Learning outcomes

Distinguish DDL from DML; create, alter and drop tables; insert rows; update and delete records safely; use transactions; and execute data changes from Python.

## 1. Two broad categories of SQL statements

Data Definition Language (DDL) defines database structures: CREATE, ALTER and DROP. Data Manipulation Language (DML) works with stored records: INSERT, UPDATE and DELETE. SELECT retrieves data and is often classified separately as DQL.

## 2. CREATE TABLE

```sql
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT,
    price REAL NOT NULL CHECK (price >= 0),
    active INTEGER NOT NULL DEFAULT 1
);
```

The schema defines column names, types and constraints. SQLite uses dynamic typing with type affinity; declared types influence storage but do not enforce rigid types in exactly the same way as some other database engines. SQLite also supports STRICT tables in sufficiently recent versions. For this course, use clear declared types and validate inputs.

## 3. INSERT

```sql
INSERT INTO products (product_name, category, price)
VALUES ('Notebook', 'Stationery', 2500);
```

List columns explicitly. If the primary key is an automatically assigned integer, it can be omitted. To insert multiple rows:

```sql
INSERT INTO products (product_name, category, price)
VALUES
    ('Pen', 'Stationery', 500),
    ('Mouse', 'Electronics', 12000);
```

## 4. UPDATE

```sql
UPDATE products
SET price = 2750
WHERE product_id = 1;
```

The WHERE clause is critical. Without it, every row is updated. Before a consequential update, run a SELECT with the same WHERE condition to inspect the target rows.

## 5. DELETE

```sql
DELETE FROM products
WHERE product_id = 3;
```

Without WHERE, every row is deleted. DELETE removes records; DROP TABLE removes the table structure itself. These are not interchangeable. Be especially cautious with commands that affect many rows.

## 6. ALTER TABLE

SQLite supports common ALTER TABLE operations such as renaming a table, renaming a column, adding a column and (in modern versions) dropping a column. More complex schema changes may require creating a replacement table, copying data, dropping the old table and renaming the new one. Always check SQLite version and back up important data before migrations.

```sql
ALTER TABLE products ADD COLUMN supplier TEXT;
```

## 7. Execute writes from Python

```python
import sqlite3

new_product = ("Desk lamp", "Home", 18500)

with sqlite3.connect("data/learning.db") as connection:
    connection.execute("""
        INSERT INTO products (product_name, category, price)
        VALUES (?, ?, ?)
    """, new_product)
```

The connection context commits a successful transaction and rolls back when an exception occurs. Use placeholders for values. Never build SQL by interpolating untrusted values into a string.

## 8. Update safely with a preview

```python
import sqlite3

product_id = 1
new_price = 2750

with sqlite3.connect("data/learning.db") as connection:
    connection.execute("PRAGMA foreign_keys = ON;")
    preview = connection.execute(
        "SELECT product_id, product_name, price FROM products WHERE product_id = ?",
        (product_id,)
    ).fetchall()
    print("Rows to change:", preview)

    if len(preview) != 1:
        raise ValueError("Expected exactly one product")

    connection.execute(
        "UPDATE products SET price = ? WHERE product_id = ?",
        (new_price, product_id)
    )
```

This example checks that the intended identifier resolves to exactly one row before changing it. In a production workflow, also validate the new price, record an audit trail where required and ensure that the transaction is committed only after all related operations succeed.

## 9. Transactions

A transaction groups changes into one logical unit. Either all changes are committed or they can be rolled back. The key ideas are BEGIN, COMMIT and ROLLBACK. Python's sqlite3 module manages transactions; its exact defaults depend on Python version and connection configuration. The connection context manager commits or rolls back an open transaction but does not itself close the connection.

```python
import sqlite3

connection = sqlite3.connect("data/learning.db")
try:
    connection.execute("BEGIN")
    connection.execute(
        "UPDATE accounts SET balance = balance - ? WHERE account_id = ?",
        (1000, 1)
    )
    connection.execute(
        "UPDATE accounts SET balance = balance + ? WHERE account_id = ?",
        (1000, 2)
    )
    connection.commit()
except Exception:
    connection.rollback()
    raise
finally:
    connection.close()
```

This transfer example is illustrative. A real transfer must validate account existence, sufficient funds, currency and business rules, and should ensure the two account updates occur atomically.

## 10. Safe change checklist

1. Confirm the database file and environment.
2. Back up important data.
3. Preview target rows with SELECT.
4. Use a narrow, tested WHERE condition.
5. Use parameter binding.
6. Wrap related changes in a transaction.
7. Check affected row counts and resulting values.
8. Roll back if validation fails.

## Guided exercises

1. Create a products table with constraints.
2. Insert three products.
3. Update one product by ID.
4. Preview and delete one test product.
5. Add a supplier column.
6. Demonstrate rollback by making a change and rolling it back.
7. Explain the difference between DELETE and DROP TABLE.

## Independent practice

Create a small inventory table. Write Python functions to insert a product, update its price and mark it inactive. Each function must use parameterised SQL, validate inputs and report how many rows were affected. Test both a valid ID and an ID that does not exist.

## Summary

DDL changes database structure; DML changes records. INSERT adds data, UPDATE modifies selected rows and DELETE removes selected rows. Transactions and careful previews reduce the risk of accidental data loss.

## Next lesson

We will study data integrity, constraints, transaction guarantees and indexes, then connect these ideas to reliable analytical workflows.