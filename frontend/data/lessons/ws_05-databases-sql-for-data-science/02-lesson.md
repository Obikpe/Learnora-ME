# Lesson 02: Setting Up Python, VS Code and SQLite

## Purpose

You will use one consistent environment for the entire course: VS Code, Python and SQLite. SQLite is not a separate server product in this workflow. Python includes the `sqlite3` standard-library module, which lets your programs create and query SQLite databases.

## Learning outcomes

You should be able to create a project folder, select a Python interpreter in VS Code, create and run a Python script, create a SQLite database, execute a SQL statement through Python and inspect returned rows.

## 1. Install and verify the tools

Install Python 3 from the official Python distribution for your operating system. During installation on Windows, enable the option to add Python to PATH if offered. Install Visual Studio Code and the Microsoft Python extension. The extension provides interpreter selection, run/debug support and Python language features. Do not install a MySQL or PostgreSQL server for this course.

Open a terminal and check:

```bash
python --version
```

On some systems the command is:

```bash
python3 --version
```

You should see a Python 3 version. If the command is not found, Python may not be installed or may not be on PATH. Restart the terminal after installation and try again.

## 2. Create a project

Create a folder named `sql_data_science`. Open that folder in VS Code using **File → Open Folder**. Create a file named `main.py`.

A project structure will gradually look like this:

```text
sql_data_science/
├── main.py
├── data/
│   └── learning.db
├── scripts/
└── notebooks/
```

For now, create the `data` folder manually. The database file will be created by Python.

## 3. Select the Python interpreter

In VS Code, open the Command Palette and choose **Python: Select Interpreter**. Select the Python 3 installation you intend to use. The selected interpreter matters because packages and code run through that environment. If VS Code says a module is missing, first confirm that the correct interpreter is selected.

SQLite support used in this course comes with Python. You do not need to install `sqlite3` using pip. It is part of the standard library.

## 4. Your first Python program

Enter and run:

```python
print("Hello, SQL and Python!")
```

Run it using the Run Python File control or the integrated terminal:

```bash
python main.py
```

If the message appears, your Python script is running. This is a Python check, not yet a database query.

## 5. Create a SQLite database

A SQLite database is commonly stored as a file. The `sqlite3.connect()` function opens a connection. If the file does not exist, SQLite creates it.

```python
import sqlite3

connection = sqlite3.connect("data/learning.db")
print("Database connection opened.")

connection.close()
```

Run the program. A `learning.db` file should appear inside `data`. A connection is the communication channel between Python and the database. Close it when you have finished using it.

**Important path note:** the relative path is interpreted from the program's current working directory, which is normally the project folder when you run the script from VS Code. If you run from a different directory, the file may be created somewhere else. Keep your project folder as the working directory.

## 6. Execute SQL from Python

The `execute()` method sends one SQL statement to SQLite. In this first example we ask SQLite to calculate a value:

```python
import sqlite3

connection = sqlite3.connect("data/learning.db")
cursor = connection.cursor()

cursor.execute("SELECT 2 + 3;")
result = cursor.fetchone()

print(result)  # (5,)

connection.close()
```

Let's unpack this:
1. `import sqlite3` makes Python's SQLite interface available.
2. `connect()` opens the database.
3. `cursor()` creates an object used to execute SQL and fetch query results.
4. `execute()` sends the SQL statement to SQLite.
5. `fetchone()` retrieves one result row.
6. `close()` closes the connection.

The result is a tuple, `(5,)`, because a query result row can contain one or more column values. The comma indicates a one-element tuple.

## 7. Create your first table

A table is created with SQL's `CREATE TABLE` statement. We will study table design later; for now, observe the relationship between the Python string and SQL statement.

```python
import sqlite3

connection = sqlite3.connect("data/learning.db")
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        programme TEXT
    );
""")

connection.commit()
connection.close()
```

`IF NOT EXISTS` prevents an error if the table is already present. `INTEGER` and `TEXT` describe the kinds of values intended for the columns. `PRIMARY KEY` identifies rows uniquely. `NOT NULL` means a name must be supplied. We will explain each rule in later lessons.

`commit()` saves a transaction's changes. Creating a table changes the database structure, so we commit it.

## 8. Inspect a table with SQL

```python
import sqlite3

with sqlite3.connect("data/learning.db") as connection:
    cursor = connection.cursor()
    cursor.execute("PRAGMA table_info(students);")
    for column in cursor.fetchall():
        print(column)
```

The `PRAGMA table_info` command is SQLite-specific and reports column information. The `with` statement manages the connection context and closes it when the block ends. We will use this safer pattern regularly.

## 9. Common setup problems

- **`python` not recognised:** verify installation and PATH; on some systems use `python3` or the Windows launcher `py`.
- **Wrong interpreter:** select the intended interpreter in VS Code.
- **Database file appears in an unexpected folder:** check the current working directory and use a deliberate project-relative path.
- **No output:** ensure the file was saved and the correct script was run.
- **Table already exists:** use `IF NOT EXISTS` for setup scripts, or inspect the existing table rather than deleting data blindly.
- **Module not found for sqlite3:** this is not normally a pip installation issue; check that you are running a standard Python distribution.

## Guided exercise

Create a file named `setup_database.py`. In it, open `data/learning.db`, create a table named `practice` with an integer primary key and a text column named `topic`, inspect its columns with `PRAGMA table_info`, print the result and close the connection.

## Independent practice

1. Create a second database file named `practice.db`.
2. Run `SELECT 10 * 4;` through Python and print the returned tuple.
3. Explain what a connection and cursor do.
4. Explain why `sqlite3` does not need to be installed using pip.
5. Deliberately run a script from a different working directory and observe where a relative database path is resolved. Then correct it.

## Lesson summary

VS Code is where you edit and run Python. Python's built-in `sqlite3` module connects to SQLite. SQLite stores data in a database file and executes the SQL statements sent by Python. This is the practical pattern we will use throughout the course.

## Next lesson

Now that the environment works, we will learn to retrieve data using `SELECT`, choose columns, use aliases and understand the shape of query results.