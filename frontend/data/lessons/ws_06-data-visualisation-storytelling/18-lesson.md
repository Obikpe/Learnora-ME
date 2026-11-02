# Lesson 18: Data Visualisation Capstone and Review

## Project brief
Create a complete visual analysis in Python using a dataset cleaned in WS04 or a relational summary produced in WS05. The project must answer a real question, use appropriate charts and communicate findings honestly.

## Learning outcomes
Plan a visual analysis, choose suitable encodings, build a consistent set of charts, assess accessibility and integrity, communicate a narrative, and deliver a reproducible Python project.

## 1. Define the project question
Write one primary question and no more than four supporting questions. State:
- audience and decision;
- unit of analysis;
- time period and population;
- important metrics and their definitions;
- data limitations that may affect interpretation.

A question such as “How did monthly completed-order revenue change?” is testable if the dataset contains order dates, status and revenue fields. “Why did revenue fall?” may require additional evidence beyond transaction records.

## 2. Prepare the analysis dataset
Use Python to load the data and inspect it:
```python
import pandas as pd

df = pd.read_csv("data/analysis_dataset.csv")
print(df.shape)
print(df.dtypes)
print(df.isna().sum())
print(df.head())
```
Confirm the row grain, date range, missingness, duplicate keys and metric definitions. Do not create charts from an unvalidated dataset.

## 3. Plan the chart set
Choose visuals based on the questions:
- trend over time: line chart;
- category comparison: sorted bar chart;
- distribution: histogram or boxplot;
- relationship: scatterplot;
- composition: stacked bar only when the components and total are meaningful.

Each chart must add a distinct piece of evidence. Do not choose a chart because it looks impressive.

## 4. Apply a consistent Python style
```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(9, 5))
ax.bar(category_summary["category"],
       category_summary["revenue"])
ax.set_title("Revenue by product category")
ax.set_xlabel("Product category")
ax.set_ylabel("Revenue (currency units)")
ax.tick_params(axis="x", rotation=30)
fig.tight_layout()
fig.savefig("outputs/category_revenue.png", dpi=200)
plt.show()
```
Use readable labels, sensible ordering, sufficient contrast and clear units. Save figures into a project output folder so they can be included in a report.

## 5. Review visual integrity
Before submitting, check:
- axes begin and end in a way that does not exaggerate differences;
- time intervals are correctly ordered and consistently spaced;
- denominators are stated for rates and percentages;
- missing values are not silently treated as zero;
- categories are not omitted without explanation;
- colour is not the only way information is encoded;
- sample sizes and uncertainty are visible where they matter;
- titles and captions match the data actually plotted.

## 6. Build the story
Use a short sequence: context, question, evidence, interpretation and action. State what the analysis cannot establish. If your data is observational, do not imply that one variable caused another merely because they move together.

## 7. Deliver a reproducible project
Suggested structure:
```text
visualisation-capstone/
    data/README.md
    notebooks/analysis.ipynb
    src/prepare_data.py
    outputs/figures/
    report.md
    README.md
    requirements.txt
```
Document where the data came from, how it can be accessed, the Python packages required and the steps to reproduce each chart. Do not publish personal or confidential source data.

## Assessment rubric
| Area | Weight | Evidence |
|---|---:|---|
| Question and audience | 10% | Clear decision context and scope |
| Data preparation | 15% | Quality checks and correct definitions |
| Chart selection | 20% | Appropriate visuals for analytical questions |
| Visual design and integrity | 20% | Readability, accessibility and honest scales |
| Story and interpretation | 20% | Evidence-led narrative and useful action |
| Reproducibility | 15% | Code, setup and outputs can be recreated |

## Submission checklist
- [ ] The question and audience are explicit.
- [ ] The data source and row grain are documented.
- [ ] Every chart answers a question.
- [ ] Labels, units, titles and captions are clear.
- [ ] Missingness and limitations are disclosed.
- [ ] No unsupported causal claims are made.
- [ ] Charts are saved and referenced in the report.
- [ ] The project can be reproduced from its README.

## Reflection
Which chart changed your understanding most? Which chart did you remove because it added little? What additional data would improve the analysis? What could a decision-maker misunderstand?

## Bridge to WS07
Visual analysis helps explain what happened and what patterns exist. Machine learning introduces a different goal: learning patterns from examples to make predictions or discover structure. The next course begins with problem framing, baselines, data splits and generalisation before building more complex models.

## Completion standard
You can turn a validated Python dataset into a coherent, accessible and reproducible visual story, while explaining what the evidence does and does not support.
