# Lesson 10: Data Cleaning Evidence and Decisions

## Learning outcomes
Apply the professional method, produce a project artefact and communicate decisions with evidence.

## 1. Core explanation
Data cleaning should be evidence-led. Start by identifying duplicate records, invalid values, inconsistent categories, impossible dates, missingness and unexpected data types. Do not remove a row simply because it is unusual. Determine whether it is an error, a valid rare case or a separate population.

Keep an audit trail of changes: original field, issue, rule applied, number of affected records and rationale. Preserve raw data separately and make cleaning repeatable in code. If you standardise categories, document the mapping. If you impute values, report the method and missingness level.

Cleaning can introduce bias. Removing incomplete records may disproportionately exclude a group. Converting unknown to zero changes the meaning. Every cleaning decision should be assessed for its effect on the analytical question and reported in the final work.

## 2. Worked example or template
Use the example in VS Code or adapt the structure to your project.

```python
import pandas as pd

raw = pd.DataFrame({
    "region": ["North", "north ", "SOUTH", None, "West"],
    "age": [22, 31, -4, 40, None],
    "customer_id": [1, 2, 3, 4, 4]
})
clean = raw.copy()
clean["region"] = clean["region"].str.strip().str.title()
clean.loc[clean["age"] < 0, "age"] = pd.NA
print("Duplicates:", clean.duplicated().sum())
print(clean)
```

## 3. Professional application
Keep the artefact reproducible and honest. State the data source, time period, methods, your contribution and limitations. Do not publish confidential data or make unsupported performance claims.

## 4. Guided practice
Create a cleaning log for the example. Identify which records need investigation rather than automatic correction. Explain how you would check whether removing missing rows changes group representation.

## 5. Independent practice
Create or improve the corresponding project artefact. Ask another person to review it and record any unclear assumptions or missing instructions.

## 6. Knowledge check
1. What decision or audience does this artefact serve?
2. What evidence supports the claim?
3. Which limitations must be disclosed?
4. How can another person verify the work?

## Lesson summary
A professional portfolio demonstrates judgement, evidence, reproducibility and communication—not just familiarity with tools.