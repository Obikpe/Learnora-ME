# Lesson 23: SQL and Python Assessment Practice

## Learning outcomes
Apply the professional practice, produce the capstone artefact and communicate evidence and limitations clearly.

## 1. Core explanation
Data roles often combine SQL reasoning with Python data manipulation. SQL questions test filtering, grouping, joins, null handling, window functions and aggregation. Python questions test data structures, functions, pandas operations, debugging and clear reasoning.

Read the question carefully and define the expected grain of the output. A join can duplicate rows if the key is not unique. Aggregation can hide missing categories. In pandas, chained assignment and implicit type conversion can produce unexpected behaviour. Check row counts before and after joins and transformations.

Explain assumptions and test edge cases. If the prompt asks for monthly active users, define “active” and the month boundary. If the dataset contains duplicate events, decide whether to deduplicate before counting. Correctness matters more than writing the shortest query.

## 2. Worked example or template
Run the Python example in VS Code where applicable. Adapt paths and fields to your own dataset; do not publish restricted records.

```python
import pandas as pd

events = pd.DataFrame({
    "user_id": [1, 1, 2, 3, 3, 3],
    "event_date": pd.to_datetime(["2026-01-02", "2026-01-12", "2026-01-05",
                                  "2026-01-03", "2026-02-02", "2026-02-08"])
})
events["month"] = events.event_date.dt.to_period("M")
monthly_active = events.groupby("month")["user_id"].nunique()
print(monthly_active)
```

## 3. Capstone application
Maintain a decision log and connect every analysis step to the project charter. Preserve provenance and reproducibility. Separate observed results from interpretation and recommendations.

## 4. Guided practice
Write a SQL query and a pandas equivalent to count distinct active users per month. Explain why COUNT(*) may give a different answer from COUNT(DISTINCT user_id).

## 5. Independent practice
Complete the corresponding capstone deliverable. Ask a reviewer to reproduce or challenge one result and record the changes made in response.

## 6. Knowledge check
1. What evidence does this deliverable provide?
2. Which assumptions or limitations affect the conclusion?
3. How can another person reproduce the work?
4. What is the next responsible action?

## Lesson summary
A capstone demonstrates an end-to-end professional process: a well-framed question, defensible data, reproducible analysis, validation, clear communication and responsible publication.