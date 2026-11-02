# Lesson 03: Retrieving Data with SELECT

## Learning outcomes

By the end of this lesson, you should be able to explain a basic query, retrieve all or selected columns, use column aliases, create calculated columns, remove duplicate result values with `DISTINCT`, and retrieve query results from Python using cursor methods.

## 1. The example database

We will use a small training-centre database throughout the early lessons. Our first table is `students`:

| student_id | name | programme | age |
|---:|---|---|---:|
| 1 | Ada | Data Science | 22 |
| 2 | Musa | Statistics | 25 |
| 3 | Tola | Data Science | 21 |
| 4 | Kemi | Business Analytics | 24 |

The table is a teaching example. You will create it from Python so that every learner can reproduce the same results.

```python
import sqlite3

students = [
    (1, "Ada", "Data Science", 22),
    (2, "Musa", "Statistics", 25),
    (3, "Tola", "Data Science", 21),
    (4, "Kemi", "Business Analytics", 24),
]

with sqlite3.connect("data/learning.db") as connection:
    connection.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            programme TEXT NOT NULL,
            age INTEGER
        )
    """)
    connection.executemany("""
        INSERT OR IGNORE INTO students
        (student_id, name, programme, age)
        VALUES (?, ?, ?, ?)
    """, students)
```

`executemany()` applies one parameterised statement to multiple records. The question marks are placeholders; values are supplied separately. This avoids constructing SQL by joining raw user input into a string. We will study safe parameterisation in depth in Lesson 17.

## 2. What is a query?

A query is a request sent to a database. A `SELECT` query retrieves data; it does not change the stored rows. The simplest query is:

```sql
SELECT * FROM students;
```

The asterisk means all columns. The `FROM` clause identifies the table. The semicolon marks the end of the SQL statement.

Run it from Python:

```python
import sqlite3

with sqlite3.connect("data/learning.db") as connection:
    cursor = connection.execute("SELECT * FROM students;")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
```

Each row is returned as a tuple. The database returns rows; Python decides how to display or further process them.

## 3. Select only the columns you need

```sql
SELECT name, programme
FROM students;
```

This returns two columns rather than every field. Selecting only required columns makes queries easier to read and can reduce the amount of data transferred. In analytical work, avoid `SELECT *` in final reusable queries when you know the required fields. A new column added later could otherwise change the output unexpectedly.

## 4. Column order matters

```sql
SELECT programme, name
FROM students;
```

The output columns appear in the order written in the `SELECT` list. The order of rows is not guaranteed unless you explicitly sort them with `ORDER BY`, which we cover in Lesson 05.

## 5. Aliases with AS

An alias gives a column or expression a temporary output name:

```sql
SELECT
    name AS student_name,
    programme AS study_programme
FROM students;
```

Aliases improve readability, especially when an expression has a long name. An alias does not rename the underlying database column; it changes the label in this query's result.

## 6. Calculated columns

SQL can calculate values as it retrieves data:

```sql
SELECT
    name,
    age,
    age + 1 AS age_next_year
FROM students;
```

For each row, SQLite adds one to the stored age and labels the calculated result `age_next_year`. The calculation is not saved back to the table. It exists in the query result only.

Try another expression:

```sql
SELECT
    name,
    age,
    age * 12 AS age_in_months
FROM students;
```

This is arithmetic on the age value, not a claim that a person's age is best represented in months for every analytical purpose. Always check whether a calculated measure has a meaningful interpretation.

## 7. DISTINCT

If many students are enrolled in the same programme, a query may return repeated programme names. Use `DISTINCT` to return unique combinations of selected columns:

```sql
SELECT DISTINCT programme
FROM students;
```

If you select two columns, uniqueness applies to the pair:

```sql
SELECT DISTINCT programme, age
FROM students;
```

This does not mean “unique programme and then unique age independently”. It means unique rows of the combined pair.

## 8. SQL keywords and formatting

SQL keywords are commonly written in uppercase for readability, but SQLite accepts lowercase keywords too. Indentation and line breaks help humans understand a query; they do not usually change its meaning. Use one clause per line and indent lists consistently.

## 9. Fetching results in Python

The cursor provides several retrieval methods:
- `fetchone()`: retrieves the next single row, or `None` when no row remains.
- `fetchmany(n)`: retrieves up to `n` next rows.
- `fetchall()`: retrieves all remaining rows into memory.

Example:

```python
with sqlite3.connect("data/learning.db") as connection:
    cursor = connection.execute(
        "SELECT name, age FROM students;"
    )
    first = cursor.fetchone()
    remaining = cursor.fetchall()

print("First:", first)
print("Remaining:", remaining)
```

Notice that after `fetchone()`, the cursor has advanced. `fetchall()` returns only the remaining rows, not the first row again. For very large results, fetching everything at once may use too much memory; later Python lessons will discuss chunking and Pandas.

## Guided practice

1. Retrieve only student names.
2. Retrieve names and ages, with the age column labelled `student_age`.
3. Calculate age five years from now.
4. List distinct programmes.
5. Run a query through Python and print each returned row on a separate line.

## Independent practice

Use the seeded `courses` table with `course_id`, `course_title` and `duration_hours`. Insert at least four courses. Write queries to retrieve all columns, retrieve only course names, calculate duration in minutes, and list distinct duration values. Explain why the calculated duration is not automatically stored in the table.

## Common mistakes

- Forgetting `FROM`: SQL needs to know which table supplies the columns.
- Writing a column name that does not exist: inspect the table schema.
- Assuming rows are sorted: only `ORDER BY` guarantees a requested order.
- Confusing an alias with a permanent column rename.
- Calling `fetchone()` and assuming a later `fetchall()` starts again from the first row.

## Lesson summary

`SELECT` retrieves data. `FROM` identifies its source. Select explicit columns when possible, use aliases for clearer output, calculate derived values when useful, and use `DISTINCT` to remove duplicate result combinations. Python fetch methods bring query results into your program.

## Next lesson

A query that returns every row is often too broad. Next we learn to filter records precisely with `WHERE`.