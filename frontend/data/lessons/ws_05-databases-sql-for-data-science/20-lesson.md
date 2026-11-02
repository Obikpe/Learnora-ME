# Lesson 20: Capstone — End-to-End SQL and Python Analytics Project

## Project purpose

This capstone brings together the course. You will design a relational database, populate it with realistic data, query it using SQL through Python, analyse results with Pandas, validate metrics and communicate findings. You will work entirely in VS Code with Python and SQLite.

## Scenario: analysing an online learning platform

An online learning platform wants to understand learner enrolment, course engagement, completion and revenue. The organisation has records about learners, courses, enrolments, learning activity and payments. Your task is to build a small analytical database and produce a defensible report.

You may generate synthetic data with Python. Clearly label it as synthetic; do not present it as real company data.

## Project outcomes

Your final submission should demonstrate that you can:
1. Design related tables and explain their keys and relationships.
2. Create a SQLite database through Python.
3. Insert data safely with parameterised statements.
4. Retrieve and filter records using SELECT and WHERE.
5. Aggregate performance using GROUP BY and HAVING.
6. Join multiple tables without duplicating measures.
7. Use subqueries or CTEs for multi-step analysis.
8. Use window functions for ranking and time comparisons.
9. Use transactions and constraints appropriately.
10. Query SQL results into Pandas.
11. Validate and reconcile results.
12. Present findings with clear metric definitions and limitations.

## Part A — Design the database

Create these tables:

**learners**
- learner_id: primary key
- learner_name: required text
- region: region or location group
- registration_date: ISO date text

**courses**
- course_id: primary key
- course_title: required text
- category: category label
- price: non-negative numeric value

**enrolments**
- enrolment_id: primary key
- learner_id: foreign key to learners
- course_id: foreign key to courses
- enrolled_on: ISO date
- status: enrolled, completed, dropped or paused
- completion_date: optional ISO date

**activity**
- activity_id: primary key
- enrolment_id: foreign key to enrolments
- activity_date: ISO date/time
- minutes_spent: non-negative numeric value

**payments**
- payment_id: primary key
- enrolment_id: foreign key to enrolments
- payment_date: ISO date
- amount: non-negative numeric value
- payment_status: pending, paid or refunded

Use constraints to prevent invalid statuses and negative durations or amounts. Decide whether one learner can enrol in the same course more than once. If not, add a UNIQUE constraint on learner_id and course_id. If re-enrolment is allowed, document the rule and model attempts separately or use an appropriate attempt identifier.

Relationship sketch:

```text
LEARNERS 1 ----< ENROLMENTS >---- 1 COURSES
                    |
                    | 1
                    +----< ACTIVITY
                    |
                    +----< PAYMENTS
```

An enrolment belongs to one learner and one course. It can have many activity records and payment records.

## Part B — Generate and load synthetic data

Use Python's `random` module or a deterministic generator with a fixed seed so the dataset can be reproduced. Generate at least:
- 100 learners across several regions.
- 8 courses across at least three categories.
- 150 enrolments with varied statuses and dates.
- Multiple activity records for many enrolments.
- Payment records including paid, pending and refunded cases.

Use a fixed random seed and document it. Use parameterised INSERT statements and executemany. Ensure foreign keys point to valid parent records. Do not create impossible dates or payments that contradict your stated scenario.

## Part C — SQL analysis questions

Write and explain queries for each task:

1. How many learners registered in each region?
2. How many enrolments does each course have?
3. What is the completion rate by course?
4. Which courses have more than a chosen minimum number of enrolments?
5. What is paid revenue by course category?
6. Which learners have never enrolled?
7. Which enrolments have no activity records?
8. What is the average time spent per completed enrolment?
9. Rank courses by paid revenue within category.
10. Calculate monthly enrolment counts and month-over-month change.
11. Find each learner's first enrolment month and calculate cohort activity by month offset.
12. Identify records with missing or inconsistent values.

For each query, state the grain of the output. For example, a course summary should have one row per course. A monthly report should have one row per month. This prevents accidental double counting.

## Part D — Python and Pandas analysis

Use Python to:
- Connect to SQLite and execute your SQL queries.
- Load selected query results into Pandas DataFrames.
- Inspect shape, data types and missing values.
- Parse date columns.
- Calculate at least one metric in SQL and independently in Pandas.
- Create at least two clear visualisations (for example, enrolments by month and paid revenue by category).
- Save a clean summary table or CSV output.

Do not load every raw table into Pandas by default. Retrieve only the columns and period required for each analysis. If a query returns a large dataset, consider chunked reading.

## Part E — Validation and interpretation

Your report must include at least five validation checks:
- Primary identifiers are unique.
- Foreign keys have no orphan records.
- Enrolment statuses are in the allowed set.
- Durations and amounts satisfy the stated rules.
- Revenue reconciles between SQL and Pandas.
- Completion-rate denominator is explicitly defined.
- Join operations have not multiplied payment amounts.
- Cohort retention uses the original cohort size as denominator.

Explain any anomalies. A high completion rate among a small course cohort may be less reliable than a similar rate among a large cohort. A missing payment record is not automatically a zero payment. Distinguish missing, pending, refunded and paid.

## Part F — Final report

Write a short analytical report with:
1. **Executive summary:** three to five evidence-based findings.
2. **Data and methods:** tables, date range, synthetic-data note and tools.
3. **Metric definitions:** numerator, denominator and inclusion rules.
4. **Results:** charts and tables with clear labels.
5. **Data quality:** checks performed and issues found.
6. **Limitations:** what the data cannot establish.
7. **Recommendations:** practical next steps supported by the analysis.

Do not claim causation from descriptive patterns. For example, a relationship between time spent and completion does not prove that additional time causes completion.

## Suggested project structure

```text
learning_platform_analysis/
├── data/
│   └── learning_platform.db
├── src/
│   ├── create_schema.py
│   ├── generate_data.py
│   ├── queries.py
│   ├── validation.py
│   └── analysis.py
├── outputs/
│   ├── figures/
│   └── report.md
├── run_project.py
└── README.md
```

## Assessment rubric

| Area | Weight |
|---|---:|
| Relational design, keys and constraints | 15% |
| Correct SQL querying, joins and aggregation | 25% |
| Advanced SQL (CTEs, subqueries, windows) | 15% |
| Python database integration and safe writes | 15% |
| Pandas analysis and visualisation | 10% |
| Validation, metric definitions and interpretation | 15% |
| Reproducibility and documentation | 5% |

## Submission checklist

- [ ] Database creation script runs from a clean environment.
- [ ] Data generation is reproducible.
- [ ] SQL statements are readable and parameterised where values are dynamic.
- [ ] Foreign keys and constraints are enabled and tested.
- [ ] All required analytical questions are answered.
- [ ] SQL and Pandas results reconcile where expected.
- [ ] Charts have titles, units and meaningful labels.
- [ ] Metric denominators and limitations are explained.
- [ ] README explains how to run the project in VS Code.
- [ ] No real personal or confidential data is included.

## Reflection questions

1. Which task was easier to express in SQL, and which was easier in Pandas?
2. What error would have caused the largest analytical distortion?
3. How did you verify that joins did not duplicate revenue?
4. What would need to change if the database grew from hundreds to millions of records?
5. Which assumptions would you confirm with a real business stakeholder?

## Course completion

By completing this project, you demonstrate the complete workflow: understand relational data, design tables, write SQL, connect Python, retrieve and transform data with Pandas, validate outputs and communicate findings. You are not expected to memorise every SQL function. You are expected to know how to reason about the data, find the relevant documentation and build reliable queries.