# Databases & SQL for Data Science

**Course ID:** ws_05  
**Duration:** 15 hours guided instruction; independent study and capstone work may take longer  
**Lessons:** 20  
**Environment:** VS Code, Python 3, SQLite, Python `sqlite3`, Pandas

## Course description

This course teaches relational databases and SQL to data science learners who will execute SQL through Python. Learners do not install or administer MySQL, PostgreSQL, SQL Server or a separate database server. The working database engine is SQLite, accessed using Python's standard-library `sqlite3` module. VS Code is the IDE.

SQL is taught as a language in its own right: learners understand what SQL is before learning its syntax and analytical uses. From the first practical setup, all SQL statements are executed through Python. Python orchestrates the workflow; SQLite stores data and executes SQL; Pandas supports downstream analysis. SQLite is a real relational database engine, but some syntax and features differ among database products. Lessons explain relevant SQLite behaviour and portability considerations.

## Learning outcomes

Learners completing this course should be able to:
1. Explain databases, DBMSs, relational tables, schemas, keys and SQL.
2. Set up Python and VS Code and create/query a SQLite database.
3. Retrieve, filter, sort, limit and transform data using SQL.
4. Summarise data with aggregates, GROUP BY, HAVING and conditional aggregation.
5. Design relational tables and apply keys, constraints and normalisation.
6. Join tables while reasoning about output grain and duplicate multiplication.
7. Combine result sets with UNION, UNION ALL, INTERSECT and EXCEPT.
8. Use subqueries, CTEs and window functions.
9. Solve segmentation, cohort, retention and trend-analysis problems.
10. Create and modify database structures and records safely.
11. Apply integrity rules, transactions, indexes and query-performance principles.
12. Connect Python to SQLite, execute parameterised SQL and handle results/errors.
13. Move data between SQL and Pandas and build repeatable analytical workflows.
14. Complete an end-to-end project and communicate findings responsibly.

## The 20-lesson learning path

### Stage 1 — Foundations and first queries
| Lesson | Topic | Key learning |
|---|---|---|
| 01 | Understanding Databases, Data and SQL | Data, databases, DBMS, relational model, tables, keys, SQL vs Python vs SQLite vs VS Code |
| 02 | Setting Up Python, VS Code and SQLite | Python setup, VS Code interpreter, project structure, sqlite3, database files and first SQL execution |
| 03 | Retrieving Data with SELECT | SELECT, FROM, explicit columns, aliases, expressions, DISTINCT and Python fetch methods |
| 04 | Filtering Data with WHERE | Comparisons, AND/OR/NOT, IN, BETWEEN, LIKE, NULL and parameter binding |
| 05 | Sorting, Limiting and Transforming Results | ORDER BY, tie-breakers, LIMIT/OFFSET, CASE, text/numeric/date functions |

### Stage 2 — Summaries and relational data
| Lesson | Topic | Key learning |
|---|---|---|
| 06 | Aggregation and Grouped Analysis | COUNT, SUM, AVG, MIN, MAX, GROUP BY, HAVING, conditional aggregation and denominators |
| 07 | Relational Design, Keys and Data Integrity | Entities, primary/foreign keys, relationship cardinality, junction tables, constraints and normalisation |
| 08 | Joining Related Tables | INNER, LEFT, RIGHT/FULL where supported, CROSS and self joins; grain, unmatched rows and row multiplication |
| 09 | Set Operations and Combining Query Results | UNION, UNION ALL, INTERSECT, EXCEPT, duplicate handling and column alignment |
| 10 | Subqueries and Common Table Expressions | Scalar, IN, EXISTS, correlated subqueries, derived tables and multi-stage CTEs |

### Stage 3 — Advanced SQL and reliable database work
| Lesson | Topic | Key learning |
|---|---|---|
| 11 | Window Functions for Analytical SQL | OVER, PARTITION BY, ordering, ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD, frames and moving averages |
| 12 | Advanced Analytical SQL: Segmentation, Cohorts and Trends | Metric definitions, RFM-style summaries, segments, cohorts, retention and trends |
| 13 | Creating Tables and Safely Changing Data | DDL/DML, CREATE, ALTER, DROP, INSERT, UPDATE, DELETE and transactions |
| 14 | Data Integrity, Transactions and Indexes | Constraints, NULL, ACID, referential integrity, indexes and data-quality checks |
| 15 | Query Performance and Optimisation | Query plans, scans/searches, indexes, efficient filters/joins and benchmarking |

### Stage 4 — SQL through Python
| Lesson | Topic | Key learning |
|---|---|---|
| 16 | Connecting Python to SQLite | sqlite3, connections, cursors, context managers, row factories, schema inspection and project structure |
| 17 | Executing SQL Safely from Python | execute, executemany, parameter binding, CRUD, transactions, rowcount, errors and SQL injection prevention |
| 18 | SQL and Pandas for Data Science | read_sql_query, to_sql, dtypes, missing values, SQL/Pandas decisions, chunks and reconciliation |
| 19 | Reusable Python–SQL Workflows and Data Pipelines | Modules, reusable functions, validation, logging, configurable date windows, idempotency and reproducibility |

### Stage 5 — Capstone
| Lesson | Topic | Key learning |
|---|---|---|
| 20 | Capstone: End-to-End SQL and Python Analytics Project | Relational design, synthetic data, SQL analysis, Pandas, validation, visualisation, reporting and limitations |

## Teaching standard

Every lesson is intended to function as a self-study resource without requiring a tutor to fill in missing explanations. Lessons introduce the problem and learning outcomes, define new terms in plain language, explain why a concept exists, start with small examples, explain code and output step by step, then progress to realistic analytical examples. Each includes common mistakes, debugging guidance, guided practice, independent exercises, a summary and a link to the next lesson. Code should be runnable or clearly labelled illustrative. The 20 lessons should use coherent schemas and build on previous concepts.

## Shared practical database

Early lessons progressively use a training-centre dataset with students/learners, courses, enrolments, assessments and activity. Customers/orders/products are introduced where business examples make a concept clearer. The capstone uses a coherent learning-platform schema with learners, courses, enrolments, activity and payments. Capstone data is synthetic and must be labelled as such.

## Environment and technical notes

- IDE: Visual Studio Code.
- Language: Python 3.
- Database engine: SQLite.
- Interface: Python standard-library `sqlite3`.
- Data analysis: Pandas.
- No separate database server or SQL client is required.
- SQLite uses dynamic typing and date/time conventions that differ from some server database systems.
- Enable foreign-key enforcement on each connection using `PRAGMA foreign_keys = ON`.
- RIGHT and FULL OUTER JOIN require SQLite 3.39.0 or later.
- SQL dialects differ; course examples focus on SQLite-compatible SQL.
- SQL placeholders bind values, not table or column identifiers. Dynamic identifiers require a validated allow-list.
- Parameterised queries protect values from SQL injection; input validation and constraints are also necessary.
- Pandas and SQL may differ in NULL/missing-value and grouping semantics; reconcile results when both are used.
- Query optimisation must be measured on representative data; an index is not automatically beneficial.

## Assessment

Practice appears throughout the course. The capstone is assessed on relational design and constraints (15%), SQL querying/joins/aggregation (25%), advanced SQL (15%), Python database integration and safe writes (15%), Pandas analysis and visualisation (10%), validation and interpretation (15%), and reproducibility/documentation (5%).

## Expected capability

A learner completing the course should be able to open a Python project in VS Code, connect to SQLite, design and query related tables, write SQL from beginner through advanced analytical patterns, safely pass parameters and modify data, load selected results into Pandas, validate findings and deliver a reproducible analytical project.