# Lesson 23: SQL and Python Assessment Practice

## Learning outcomes

By the end of this lesson, you should be able to answer a monthly-active-user assessment with SQL and pandas; define activity and time grain; count distinct users; and explain how duplicate events and date boundaries affect results.

## 1. Core explanation

Data roles often combine SQL reasoning with Python data manipulation. SQL questions test filtering, grouping, joins, null handling, window functions and aggregation. Python questions test data structures, functions, pandas operations, debugging and clear reasoning.

Read the question carefully and define the expected grain of the output. A join can duplicate rows if the key is not unique. Aggregation can hide missing categories. In pandas, chained assignment and implicit type conversion can produce unexpected behaviour. Check row counts before and after joins and transformations.

For monthly active users (MAU), define what counts as an activity and whether a user is counted once per calendar month or once per rolling 30-day period. Here, an active user is a distinct user with at least one qualifying event during a calendar month. Multiple events by the same user in the same month count once.

## 2. Worked example: SQL and pandas equivalents

Run in VS Code. Install pandas with `python -m pip install pandas`. SQLite is included with Python; no database server is required.

```python
import sqlite3
import pandas as pd

events = [
    (1, "2026-01-02", "login"),
    (2, "2026-01-05", "purchase"),
    (1, "2026-01-12", "view"),
    (3, "2026-01-03", "login"),
    (3, "2026-02-02", "login"),
    (3, "2026-02-08", "purchase"),
    (2, "2026-02-11", "login"),
]

with sqlite3.connect(":memory:") as connection:
    connection.execute("""
        CREATE TABLE events (
            event_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            event_date TEXT NOT NULL,
            event_type TEXT NOT NULL
        )
    """)
    connection.executemany(
        "INSERT INTO events (user_id, event_date, event_type) VALUES (?, ?, ?)",
        events
    )

    sql_result = pd.read_sql_query("""
        SELECT
            strftime('%Y-%m', event_date) AS month,
            COUNT(DISTINCT user_id) AS monthly_active_users
        FROM events
        GROUP BY strftime('%Y-%m', event_date)
        ORDER BY month
    """, connection)

print("SQL result:")
print(sql_result)

# The equivalent pandas calculation uses the same rows and calendar-month grain.
df = pd.DataFrame(events, columns=["user_id", "event_date", "event_type"])
df["event_date"] = pd.to_datetime(df["event_date"], errors="raise")
df["month"] = df["event_date"].dt.to_period("M")
pandas_result = (
    df.groupby("month")["user_id"]
      .nunique()
      .rename("monthly_active_users")
      .reset_index()
)
print("Pandas result:")
print(pandas_result)
```

Both approaches should return two active users for January 2026 and two for February 2026. The event rows are not the same as active users: user 1 has two January events but contributes one active user for January.

## 3. Important edge cases

- **Duplicate events:** repeated events by one user should not increase a distinct-user count.
- **Month boundaries:** 31 January and 1 February belong to different calendar months.
- **Time zones:** if timestamps include time zones, convert them to the agreed reporting timezone before assigning calendar months.
- **Qualifying events:** a page view, login and purchase may not all count as activity. Confirm the business definition.
- **Missing IDs:** records without a user ID cannot be attributed to a distinct user; report how many were excluded.
- **Join multiplication:** joining event rows to a one-to-many lookup table can duplicate events. Validate the join key and output grain before counting.

## 4. Guided practice

1. Add a second January event for user 2. Confirm that January MAU does not increase.
2. Add a new user with a February event. Confirm that February MAU increases by one.
3. Add an event with a missing user ID and decide how it should be reported.
4. Write a SQL query and a pandas equivalent to count events per month. Explain why that result differs from MAU.
5. Add a filter for qualifying event types and explain how the definition changes the metric.

## 5. Independent practice

Use a dataset with user IDs and timestamps. Produce calendar-month active users using both SQL and pandas. Include a data-quality summary, define the timezone and qualifying event rules, compare the outputs and explain any difference. Save the query, Python script and a short metric-definition note in your portfolio repository.

## 6. Knowledge check

1. Why is COUNT(DISTINCT user_id) different from COUNT(*)?
2. What does one row represent before and after the monthly aggregation?
3. Why must the reporting timezone be agreed before assigning events to months?
4. How can a join accidentally inflate an active-user metric?

## Lesson summary

A correct analytical answer starts with the metric definition and the grain of the data. SQL and pandas should produce the same result when they use the same records, filters, timezone and aggregation rules.