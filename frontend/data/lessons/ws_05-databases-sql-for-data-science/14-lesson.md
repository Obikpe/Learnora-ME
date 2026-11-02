# Lesson 14: Data Integrity, Transactions and Indexes

## Learning outcomes

Explain entity and referential integrity; apply constraints; understand ACID transactions; diagnose NULL and duplicate problems; create and inspect indexes; and understand why indexes improve some queries but add costs elsewhere.

## 1. Data integrity

Data integrity means data remains accurate, valid and internally consistent. It is not enough for a query to run without error. A database containing duplicate customer IDs, invalid scores or enrolments referencing nonexistent students can produce convincing but incorrect reports.

Three useful ideas:
- Entity integrity: each row can be identified reliably, commonly through a primary key.
- Referential integrity: references between tables point to valid related records.
- Domain integrity: values satisfy rules for the field, such as an allowed score range.

## 2. Constraints as database-level rules

```sql
CREATE TABLE learners (
    learner_id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    age INTEGER CHECK (age >= 0),
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'paused', 'completed'))
);
```

Constraints protect the data even if it is inserted by a different Python script. They do not replace application validation: Python should still provide helpful error messages before attempting invalid writes.

## 3. NULL, uniqueness and missingness

NULL represents missing or unknown information. It is not equal to any ordinary value, including another NULL. UNIQUE constraints in SQLite allow multiple NULL values because NULL values are treated as distinct for uniqueness purposes. If a field is mandatory, use NOT NULL as well as UNIQUE.

Do not automatically replace missing values with zero. Ask why the value is missing and whether zero is a meaningful observation.

## 4. ACID transactions

ACID describes four transaction properties:
- **Atomicity:** a transaction's changes succeed together or are rolled back.
- **Consistency:** a transaction moves the database from one valid state to another, assuming constraints and application rules are correctly defined.
- **Isolation:** concurrent transactions should not interfere in ways that violate the isolation guarantees of the engine.
- **Durability:** committed changes persist according to the database's durability guarantees.

SQLite serialises writes and has journaling modes that affect concurrency and durability behaviour. WAL mode can improve reader/writer concurrency in some workloads, but it does not make SQLite a multi-writer server database. For this course's local learning workflow, the default configuration is sufficient.

## 5. Transactions in Python

```python
import sqlite3

connection = sqlite3.connect("data/learning.db")
try:
    connection.execute("BEGIN")
    connection.execute(
        "INSERT INTO audit_log(action) VALUES (?)",
        ("price update started",)
    )
    connection.execute(
        "UPDATE products SET price = ? WHERE product_id = ?",
        (3000, 1)
    )
    connection.commit()
except sqlite3.Error:
    connection.rollback()
    raise
finally:
    connection.close()
```

This ensures the audit record and update are part of one transaction. If either statement fails, rollback prevents a partial committed change. The example assumes the audit_log table exists.

## 6. What is an index?

An index is a data structure that helps the database find rows without scanning every row in a table. Think of a book index: instead of reading every page, you use the index to locate the topic. A database index stores indexed values and references to matching rows.

```sql
CREATE INDEX idx_orders_customer_id
ON orders(customer_id);
```

An index can help queries that filter or join on customer_id. A composite index can support multiple columns:

```sql
CREATE INDEX idx_orders_region_date
ON orders(region, order_date);
```

Column order matters. An index on (region, order_date) is generally useful for searches beginning with region, and may help region plus date conditions. It is not automatically equivalent to an index on (order_date, region).

## 7. Index costs and limitations

Indexes use disk space and must be maintained when rows are inserted, updated or deleted. Too many indexes slow writes and increase storage. A query that returns a large fraction of a table may be faster with a table scan. Low-cardinality columns are not always good standalone indexes. Indexes should be designed around actual query patterns and verified with query plans.

## 8. Inspect query plans

```python
import sqlite3

with sqlite3.connect("data/learning.db") as connection:
    plan = connection.execute("""
        EXPLAIN QUERY PLAN
        SELECT order_id, amount
        FROM orders
        WHERE customer_id = ?
    """, (42,)).fetchall()

for item in plan:
    print(item)
```

Look for whether SQLite reports a table scan or index search. Query-plan output is engine-specific and can change between versions. Do not treat one plan label as a universal performance score.

## 9. Data-quality checks in SQL

Examples:
- Duplicate business identifiers: GROUP BY identifier HAVING COUNT(*) > 1.
- Missing required values: WHERE field IS NULL.
- Orphan foreign keys: LEFT JOIN parent WHERE parent key IS NULL.
- Invalid numeric ranges: WHERE score < 0 OR score > 100.
- Unexpected category values: SELECT DISTINCT category.

Data-quality checks should be written as repeatable queries, not only performed by visual inspection.

## Guided exercises

1. Add a CHECK constraint for non-negative inventory.
2. Demonstrate a UNIQUE constraint violation.
3. Insert an invalid foreign key with enforcement enabled and observe the error.
4. Create an index on a frequently filtered column.
5. Compare EXPLAIN QUERY PLAN before and after the index.
6. Explain why an index can slow an insert.

## Independent practice

Create a small orders database with customers and order items. Add primary and foreign keys, uniqueness and domain constraints. Write five data-quality checks. Create one index based on a real query pattern and use EXPLAIN QUERY PLAN to investigate whether SQLite uses it. Document both the benefit and the cost.

## Summary

Integrity is a property of the data model and workflow. Constraints protect valid values and relationships. Transactions make related changes atomic. Indexes can speed up retrieval but consume space and add write overhead; use query plans and representative workloads to evaluate them.

## Next lesson

We will bring the SQL techniques together to understand query performance and write efficient, maintainable analytical queries.