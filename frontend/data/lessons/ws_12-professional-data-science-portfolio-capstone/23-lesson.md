# Lesson 23: SQL and Python Assessment Practice

## Learning outcomes
Apply the professional practice, produce a project artefact and communicate decisions with evidence.

## 1. Core explanation
Data roles often combine SQL reasoning with Python data manipulation. SQL questions test filtering, grouping, joins, null handling, window functions and aggregation. Python questions test data structures, functions, pandas operations, debugging and clear reasoning.

Read the question carefully and define the expected grain of the output. A join can duplicate rows if the key is not unique. Aggregation can hide missing categories. In pandas, chained assignment and implicit type conversion can produce unexpected behaviour. Check row counts before and after joins and transformations.

Explain assumptions and test edge cases. If the prompt asks for monthly active users, define active and the month boundary. If the dataset contains duplicate events, decide whether to deduplicate before counting. Correctness matters more than writing the shortest query.

## 2. Worked example or template
Use the example as a starting point and adapt it to your own project. Python examples run in VS Code; shell commands should be entered in the VS Code terminal.

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

## 3. Professional application
Keep claims evidence-based. Document sources, assumptions, licences, decisions and limitations. A portfolio project should be understandable and reproducible without access to private data or undocumented local files.

## 4. Guided practice
Write a SQL query and a pandas equivalent to count distinct active users per month. Explain why COUNT(*) may differ from COUNT(DISTINCT user_id).

## 5. Independent practice
Create or improve the corresponding project artefact in your repository. Ask another person to review it and record what was unclear or incomplete.

## 6. Knowledge check
1. What is the purpose of this professional practice?
2. What evidence should be preserved?
3. Which risks or constraints need to be disclosed?
4. How will another person verify the work?

## Lesson summary
Professional data science combines sound analysis with ethical judgement, reproducible practice and clear communication.