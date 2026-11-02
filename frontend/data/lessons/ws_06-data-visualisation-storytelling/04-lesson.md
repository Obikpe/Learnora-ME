# Lesson 4: Visualisation with Matplotlib

## Learning outcomes
By the end of this lesson, you should be able to explain the central ideas, select an appropriate method, implement it in Python, interpret the output and identify limitations.

## 1. Concepts and reasoning
Matplotlib separates a Figure (the whole canvas) from Axes (the plotting area). The reliable object-oriented pattern is to create them with subplots, draw using methods such as plot, bar or scatter, configure labels and limits, then display or save the figure.

Keep data preparation separate from plotting so values can be inspected before drawing. Sort time-series records by date. Sort category values when ranking is the message. Use a deliberate figure size, readable tick labels and meaningful units. If labels overlap, adjust the layout rather than shrinking text until it becomes unreadable.

A chart that renders is not automatically interpretable. Default axis labels, unexplained abbreviations and missing units make a chart difficult to reuse. Save a final figure with a descriptive filename and sufficient resolution for the report in which it will appear.

## 2. Worked example
Run this in VS Code. Install the required libraries if they are not already available: `python -m pip install pandas matplotlib seaborn`.

```python
import pandas as pd
import matplotlib.pyplot as plt

monthly = pd.DataFrame({
    "month": ["Jan", "Feb", "Mar", "Apr"],
    "orders": [42, 51, 47, 63]
})
fig, ax = plt.subplots(figsize=(7, 4), layout="constrained")
ax.bar(monthly["month"], monthly["orders"])
ax.set_title("Orders received by month")
ax.set_xlabel("Month")
ax.set_ylabel("Number of orders")
ax.set_ylim(0, 70)
ax.grid(axis="y", alpha=0.2)
plt.show()
fig.savefig("orders_by_month.png", dpi=160, bbox_inches="tight")
```

## 3. Interpreting the output
Describe the variables and units shown. Separate what the data visibly demonstrates from your explanation of why it happened. Check whether the axes, ordering, missing values and sample size could change the interpretation. A visual pattern is a clue for further analysis, not a substitute for checking the data.

## 4. Guided practice
Recreate the chart as a line chart. Explain which chart better communicates monthly change and which better communicates discrete monthly totals. Save both charts and compare readability at presentation size.

## 5. Independent practice
Use a dataset with at least two meaningful variables. Write the analytical question before plotting. Inspect data types and missing values, make a chart, and write a short interpretation with one limitation and one follow-up question.

## 6. Knowledge check
1. Which data types are involved?
2. What question does this chart or technique answer?
3. What would make the result misleading?
4. What additional evidence would strengthen your interpretation?

## Lesson summary
A good visualisation makes the intended comparison easy, labels its scales and units, and does not imply more certainty than the data supports.