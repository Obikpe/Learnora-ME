# Lesson 01: Understanding Databases, Data and SQL

## Why this lesson matters

Data science work often begins with data that already lives somewhere: a business application, a research system, a transaction platform, a learning-management system or a collection of files. Before analysing that data, you need to understand how it is stored and how to ask for the information you need. SQL is one of the most widely used languages for this purpose.

This lesson establishes the vocabulary and mental model used throughout the course. We will not begin by asking you to memorise commands. First, understand the problem SQL solves.

## Learning outcomes

By the end, you should be able to explain what data, a database, a DBMS, a relational database, a table, a record, a field and SQL mean; distinguish SQL from Python and SQLite; describe relational keys and relationships at a high level; and explain why data scientists query databases.

## 1. What is data?

Data is a recorded representation of facts, observations, events or measurements. A student's score, a product price, a timestamp, a sensor reading and a customer's location are all data. A single value is rarely useful without context. The value `82` could mean an exam score, age, temperature or quantity sold. A good data system stores the value alongside information that explains what it represents.

A *dataset* is an organised collection of related data. A spreadsheet containing student names, courses and scores is a dataset. A database can contain many related datasets and rules governing how they fit together.

## 2. What is a database?

A database is an organised collection of data stored so that it can be accessed, managed, updated and queried. Think of a library: books are organised, catalogued and retrievable. A database performs a similar job for digital information, but it also supports rules, relationships, concurrent access and controlled changes.

A database is not necessarily a spreadsheet. Spreadsheets are useful for small, flexible tasks, but databases are designed to manage structured information reliably as it grows and is used by multiple processes.

## 3. What is a DBMS?

A database management system (DBMS) is software that manages databases. It stores data, accepts requests, enforces rules, controls access and helps keep data consistent. Examples include SQLite, PostgreSQL, MySQL and Microsoft SQL Server.

In this course we use SQLite through Python. SQLite is an embedded relational database engine: the database is stored in a file and Python can communicate with it using its built-in `sqlite3` module. There is no separate database server to install or administer for our classroom workflow.

## 4. What is SQL?

SQL stands for Structured Query Language. It is a language for working with relational databases. SQL lets us describe the data we want, define database structures and, when authorised, insert, change or delete records.

SQL is declarative. In many queries, you describe *what result you want*, and the database engine determines how to retrieve it. Python is a general-purpose programming language: it controls application logic, files, analysis and workflows. SQL and Python therefore complement each other rather than compete.

Example of a SQL request:

```sql
SELECT name, score
FROM students
WHERE score >= 70;
```

Read it as: return the name and score columns from the students table, but only for rows whose score is at least 70. Do not worry about memorising the syntax yet; each part will be taught carefully in later lessons.

## 5. SQL, Python, SQLite and VS Code: four different roles

- **SQL:** the query language used to express database operations.
- **Python:** the programming language that runs our workflow and sends SQL statements to the database.
- **SQLite:** the database engine that stores the data and executes SQL.
- **VS Code:** the IDE (integrated development environment) where we edit Python files, run programs and inspect results.

The workflow is:

```text
You write Python in VS Code
          |
          v
Python's sqlite3 module sends SQL
          |
          v
SQLite executes the SQL against a database file
          |
          v
Rows / results return to Python
          |
          v
Python displays, validates or analyses the results
```

The diagram is a flow of responsibility. VS Code does not execute SQL itself; it runs Python. Python's database interface communicates with SQLite. SQLite executes the SQL.

## 6. What is a relational database?

A relational database stores data in tables and represents connections between tables through keys. A table describes one kind of thing, such as students, courses or enrolments.

A table is made of:
- **Columns:** named attributes, such as `student_id`, `name` or `email`.
- **Rows:** individual records, such as one student's details.
- **Cell:** one value at the intersection of a row and column.
- **Schema:** the defined structure of a database, including tables, columns, data types and constraints.

Example:

| student_id | name | programme |
|---:|---|---|
| 1 | Ada | Data Science |
| 2 | Musa | Statistics |
| 3 | Tola | Data Science |

One row represents one student. One column represents one attribute shared by all student records.

## 7. Why not put everything in one enormous table?

Imagine recording students, courses, tutors and enrolments in one table. A student's name might be repeated for every course they take. If their name changes, multiple rows must be updated. A typing mistake could make one student appear to be two people. This is a data integrity problem.

Relational design separates distinct entities into tables and connects them using identifiers. We will study this in detail in Lesson 07. For now, remember that relationships help reduce unnecessary repetition and make data more reliable.

## 8. Keys: the first idea

A *primary key* uniquely identifies a row in a table. For example, two students can share the same name, so a student ID is a safer identifier. A *foreign key* is a column (or set of columns) that refers to a key in another table. It expresses a relationship between records.

A name is usually a poor key because it may not be unique and can change. A stable ID is better.

## 9. Why data scientists need SQL

Data scientists often work with datasets too large or too frequently updated for manual spreadsheet extraction. SQL can filter data close to where it is stored, join related tables, calculate summaries and select only the columns needed. Python can then handle statistical analysis, machine learning, visualisation and automation.

A sensible workflow is not “load every table into Python and hope memory is enough”. It is often better to use SQL to select and prepare the relevant records, then transfer the result into Pandas for further analysis.

## Check your understanding

1. Explain the difference between a database and a DBMS.
2. What does SQL stand for, and what kind of work is it designed for?
3. Explain the different roles of SQL, Python, SQLite and VS Code.
4. In a student table, what is the difference between a row and a column?
5. Why might a student ID be a better primary key than a student's name?

## Guided thinking exercise

A training organisation stores students, courses, tutors and assessment scores. Write down which details belong naturally to each of those four subjects. Identify one value that could uniquely identify each student and explain why names alone may not work.

## Independent practice

Find a familiar dataset (a class register, a public CSV or a small table you create). Identify its rows, columns, possible primary key and any repeated information. Do not write SQL yet. Your goal is to describe the structure accurately.

## Lesson summary

A database stores organised data. A DBMS manages it. A relational database organises data into related tables. SQL is the language used to work with relational data. In this course, Python will send SQL to SQLite, and you will write and run that Python code in VS Code.

## Next lesson

We will prepare the Python workspace in VS Code, create a SQLite database file and inspect it from Python. You will execute your first SQL statement through Python.