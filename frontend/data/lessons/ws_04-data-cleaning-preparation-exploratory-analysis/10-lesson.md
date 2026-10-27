# Lesson 10 - Cleaning Text and Standardising Categories

Course: ws_04 — Data Cleaning, Preparation & Exploratory Analysis  
Level: Beginner to intermediate  
Suggested duration: 40–50 minutes

## Learning goal
Standardise whitespace, casing and labels without erasing real distinctions.

By the end, explain the idea plainly, apply it with Python and Pandas, validate the result and describe the practical consequences.

## 1. Understand the idea
'Lagos', ' lagos ' and 'LAGOS' may refer to the same place. Trim and normalise, then inspect unique values before mapping synonyms.

Think of cleaning as checking ingredients before cooking. A mislabelled ingredient or one counted twice can spoil the result even if it looks fine. The goal is not to make data look neat at any cost; it is to make it fit the question while preserving evidence and documenting uncertainty.

## 2. Real-world example
A dashboard may show 'Online', 'online' and 'Online ' as separate channels.

Before changing a value, ask what the field means in the real process, what evidence supports the change and how you will verify it improved the data rather than hiding a problem.

## 3. Try it in Python
Install dependencies if needed: `pip install pandas matplotlib openpyxl`. Load your own dataset and adapt the column names.

```python
import pandas as pd

df['city_clean'] = df['city'].astype('string').str.strip().str.title()
print(df['city_clean'].value_counts(dropna=False))
df['channel_clean'] = df['channel'].astype('string').str.strip().str.lower()
df['channel_clean'] = df['channel_clean'].replace({'e-commerce':'online','web':'online'})
```

### Read the output, do not just run the code
- Compare the result with expected row and column counts.
- Inspect affected records, not only totals.
- Investigate surprising values before continuing.
- Keep the raw data unchanged and document assumptions.

## 4. Common mistakes
- Treating every unusual value as an error without context.
- Changing or deleting records without recording the reason.
- Assuming successful code execution proves correctness.
- Reporting a statistic without saying which records were included.

## 5. Guided practice
Use shop orders, customer records, student results or delivery data. State what one row represents. Count affected records before changing anything, apply the method and compare before/after results. Mark unresolved issues as unresolved rather than inventing values.

## 6. Assignment
Show category counts before and after and justify each mapping.

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
