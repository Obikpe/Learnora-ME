# Lesson 27 - End-to-End Cleaning and EDA Project

Course: ws_04 — Data Cleaning, Preparation & Exploratory Analysis  
Level: Beginner to intermediate  
Suggested duration: 40–50 minutes

## Learning goal
Apply the workflow to real data and deliver transparent findings.

By the end, explain the idea in plain language, apply it with Python/Pandas, validate the result and describe its practical consequences.

## 1. Understand the idea
A deliverable defines the question and row grain, documents quality issues and decisions, presents analysis and charts, and states limitations. Separate observations from explanations.

Think of cleaning as checking ingredients before cooking. A mislabelled ingredient or one counted twice can spoil the result even if it looks fine. The aim is not to make data look neat at any cost; it is to make it fit the question while preserving evidence and documenting uncertainty.

## 2. Real-world example
For e-commerce data, clarify whether rows are orders, items or payments before analysing revenue or delivery performance.

Before changing a value, ask what the field means in the real process, what evidence supports the change and how you will verify that it improved the data rather than hiding a problem.

## 3. Try it in Python
Install dependencies if needed: `pip install pandas matplotlib openpyxl`. Load your dataset first and adapt the column names.

```python
import pandas as pd

# Preserve raw files; profile quality; clean with documented rules;
# verify counts; explore distributions and segments; export charts and report.
assert clean.columns.is_unique
print(clean.shape)
print(clean.isna().sum().sort_values(ascending=False).head(10))
```

### Read the output, do not just run the code
- Compare results with expected row and column counts.
- Inspect affected records, not only totals.
- Investigate surprising values before continuing.
- Keep raw data unchanged and document assumptions.

## 4. Common mistakes
- Treating every unusual value as an error without context.
- Changing or deleting records without recording the reason.
- Assuming successful code execution proves correctness.
- Reporting a statistic without stating which records were included.

## 5. Guided practice
Use shop orders, customer records, student results or delivery data. State what one row represents. Count affected records before changing anything, apply the method and compare before/after results. Mark unresolved issues as unresolved rather than inventing values.

## 6. Assignment
Submit a notebook/script, cleaned data, quality log, four charts, five findings, three recommendations and limitations.

### Required deliverables
1. Python code or notebook with comments.
2. Explanation of the method and why it fits.
3. Evidence of results, such as counts, a table or chart.
4. A limitation, side effect or issue needing investigation.

## 7. Self-check
- [ ] Explain the concept without reading the notes.
- [ ] Apply the method with Pandas.
- [ ] Inspect examples and validate output.
- [ ] Explain effects on interpretation or downstream decisions.
- [ ] Reproduce the result and document assumptions.

## Key takeaway
Good analysis depends on careful questions, defensible rules and checks that expose mistakes. Cleaning makes data trustworthy enough for the question while being honest about uncertainty.
