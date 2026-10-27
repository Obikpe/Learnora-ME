# Lesson 06 - Data Quality Dimensions and Profiling

Course: ws_04 — Data Cleaning, Preparation & Exploratory Analysis  
ID: ws_04_l06  
Level: Beginner to intermediate  
Suggested duration: 40–50 minutes

## Learning goal
Profile completeness, validity, uniqueness, consistency and accuracy.

By the end, you should explain the idea plainly, apply it with Python and Pandas, validate the result and communicate the practical consequence of your choice.

## 1. Understand the idea
Completeness checks whether values exist; validity checks allowed rules; uniqueness checks duplicate records; consistency checks agreement; accuracy asks whether data reflects reality. Valid-looking data can still be inaccurate.

Think of data cleaning as checking ingredients before cooking. If an ingredient is mislabelled or counted twice, the dish may look fine but still be wrong. The aim is not to make data look neat at any cost; it is to make it fit for a defined purpose while preserving evidence and documenting uncertainty.

## 2. Real-world example
A date 2026-02-30 is present but invalid. Two complete records may still violate uniqueness if there should be one row per customer.

Before changing any value, ask: What does this field mean in the real process? What evidence supports the change? How will I verify the change improved the data rather than hiding a problem?

## 3. Try it in Python
Install dependencies if needed: `pip install pandas matplotlib openpyxl`. Load your own data first and adapt sample column names.

```python
import pandas as pd

profile = pd.DataFrame({'dtype':df.dtypes.astype(str),'missing':df.isna().sum(),'missing_pct':(df.isna().mean()*100).round(2),'unique':df.nunique()})
print(profile.sort_values('missing_pct',ascending=False))
```

### Read the output, do not just run the code
- Check output against expected row and column counts.
- Inspect affected records, not only the final count.
- Check how missing values, unusual values and categories are represented.
- Investigate surprising results before proceeding.

## 4. Common mistakes
- Treating every unusual value as an error without checking context.
- Deleting or changing data without recording the reason or preserving source values.
- Assuming successful code execution proves the result is correct.
- Reporting an average or percentage without stating which records were included.

## 5. Guided practice
Use a small dataset such as shop orders, student results, customer records or delivery transactions. State what one row represents. Count records affected before changing anything, apply the method, then compare before and after. Mark unresolved issues as unresolved rather than inventing values.

## 6. Assignment
Create a quality profile and write one measurable rule for each relevant quality dimension.

### Required deliverables
1. Python code or notebook with clear comments.
2. Explanation of the method and why it fits the data.
3. Evidence of the result, including counts or a table/chart where useful.
4. A limitation, possible side effect or issue requiring further investigation.

## 7. Self-check
- [ ] Explain the concept without reading the notes.
- [ ] Apply the method with Pandas.
- [ ] Inspect examples and validate the output.
- [ ] Explain the effect on interpretation or downstream decisions.
- [ ] Reproduce the result and document assumptions.

## Key takeaway
Good analysis depends on careful questions, defensible rules and checks that expose mistakes. Cleaning is not simply deleting imperfect rows; it is making data trustworthy enough for the question while being honest about what remains uncertain.
