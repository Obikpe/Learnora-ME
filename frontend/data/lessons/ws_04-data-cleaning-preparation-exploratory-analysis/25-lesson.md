# Lesson 25 - Visualisation Choices and Honest Charts

Course: ws_04 — Data Cleaning, Preparation & Exploratory Analysis  
Level: Beginner to intermediate  
Suggested duration: 40–50 minutes

## Learning goal
Choose charts that fit the question and communicate results fairly.

By the end, explain the idea in plain language, apply it with Python/Pandas, validate the result and describe its practical consequences.

## 1. Understand the idea
Bars compare categories, histograms show distributions, lines show time trends and scatterplots show relationships. Use clear labels and axes.

Think of cleaning as checking ingredients before cooking. A mislabelled ingredient or one counted twice can spoil the result even if it looks fine. The aim is not to make data look neat at any cost; it is to make it fit the question while preserving evidence and documenting uncertainty.

## 2. Real-world example
Monthly revenue is usually better shown as a line chart than a pie chart because time order matters.

Before changing a value, ask what the field means in the real process, what evidence supports the change and how you will verify that it improved the data rather than hiding a problem.

## 3. Try it in Python
Install dependencies if needed: `pip install pandas matplotlib openpyxl`. Load your dataset first and adapt the column names.

```python
import pandas as pd

monthly=df.groupby('order_month',as_index=False)['amount'].sum().sort_values('order_month')
plt.figure(figsize=(9,4)); plt.plot(monthly['order_month'],monthly['amount'],marker='o')
plt.xlabel('Month'); plt.ylabel('Revenue (NGN)'); plt.title('Monthly revenue')
plt.xticks(rotation=45); plt.tight_layout(); plt.show()
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
Create three charts and explain their suitability and caveats.

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
