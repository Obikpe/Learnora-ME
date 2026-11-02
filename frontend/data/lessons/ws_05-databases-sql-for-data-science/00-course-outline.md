# Databases & SQL for Data Science
Course: ws_05
Level: Beginner to advanced
Duration: 15h • 20 lessons
Prerequisite: WS01–WS04; basic Python and Pandas

## Course purpose
Teach relational databases and analytical SQL while keeping every practical activity inside Python. Learners use VS Code, Python's built-in sqlite3 module and SQLite database files; no separate database server or database workbench is required. SQL is a language, SQLite is the relational database engine, sqlite3 is Python's interface, and Pandas is used after query results are retrieved.

## Learning outcomes
Explain relational database concepts; inspect schemas; create and query tables; filter, sort and aggregate; design keys and relationships; join tables; use set operations, subqueries, CTEs and window functions; manage transactions and indexes; parameterise queries safely; retrieve results into Pandas; validate data; and build reproducible Python-based SQL analysis.

## Environment and teaching rules
Use Python 3, VS Code, sqlite3, Pandas and SQLite files. All SQL is executed from Python scripts or notebooks. Examples use SQLite-compatible SQL and identify dialect limitations. Use parameter binding for values. Explain code line by line and maintain a consistent sales dataset across lessons.

## Lesson sequence
01. Databases, Relational Thinking and the Role of SQL — why databases exist, tables/rows/columns, relational model, SQL categories, database vs engine vs language.
02. Python, VS Code and SQLite Setup — project setup, virtual environments, sqlite3, database files, connections, safe lifecycle and schema inspection.
03. Retrieving Data with SELECT — projections, aliases, expressions, DISTINCT, result shape and query execution from Python.
04. Filtering Data with WHERE — comparisons, logical operators, IN, BETWEEN, LIKE, NULL and correct predicate logic.
05. Sorting, Limiting and Transforming Results — ORDER BY, LIMIT/OFFSET, expressions, CASE, text/numeric operations.
06. Aggregation and Grouped Analysis — COUNT/SUM/AVG/MIN/MAX, GROUP BY, HAVING, grain and aggregate interpretation.
07. Relational Design, Keys and Data Integrity — entities, primary/foreign keys, candidate keys, constraints, normalisation and relationships.
08. Joining Related Tables — inner/left joins, join cardinality, unmatched rows, multi-table joins and validation.
09. Set Operations and Combining Query Results — UNION/UNION ALL, INTERSECT, EXCEPT, column compatibility and deduplication.
10. Subqueries and Common Table Expressions — scalar/list subqueries, correlated subqueries, CTEs, readable analytical queries.
11. Window Functions for Analytical SQL — OVER, PARTITION BY, ORDER BY, ranking, running totals, LAG/LEAD and frames.
12. Advanced Analytical SQL: Segmentation, Cohorts and Trends — conditional aggregation, cohort logic, retention-style summaries and date analysis.
13. Creating Tables and Safely Changing Data — CREATE/ALTER/DROP, INSERT/UPDATE/DELETE, CRUD, constraints and safe predicates.
14. Data Integrity, Transactions and Indexes — ACID concepts, commit/rollback, foreign-key enforcement, index trade-offs.
15. Query Performance and Optimisation — query plans, EXPLAIN QUERY PLAN, selective filters, indexes, avoiding needless work.
16. Connecting SQL Results to Pandas — read_sql_query, parameterised reads, types, SQL vs Pandas responsibilities, to_sql.
17. Building Reproducible SQL Workflows in Python — reusable functions, connection lifecycle, project structure, validation and repeatability.
18. Data Quality, Security and Responsible Database Analysis — nulls, duplicates, integrity checks, injection prevention, privacy and quality logs.
19. End-to-End SQL and Python Analytical Case Study — integrated business questions, joins, aggregates, validation, interpretation and exports.
20. Course Project, Assessment and Next Steps — independent capstone, rubric, knowledge check and bridge to Python visualisation.

## Assessment
Exercises in every lesson; progressive SQL query challenges; a data-quality audit; and a final project containing at least eight meaningful queries, a Python workflow, Pandas analysis, three charts, a written report and limitations.

## Completion standard
Learners can independently inspect a relational database, write and explain SQL from Python, validate joins and metrics, move results into Pandas and produce a reproducible analytical report.
