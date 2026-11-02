# Lesson 3: Choosing the Right Chart

## Learning outcomes
By the end of this lesson, you should be able to explain the central ideas, select an appropriate method, implement it in Python, interpret the output and identify limitations.

## 1. Concepts and reasoning
Select a chart by matching the analytical question to the data structure. A bar chart compares categories; a line chart shows an ordered time sequence; a histogram shows a numerical distribution; a scatter plot examines two numerical variables; a box plot compares distributions across groups; and a heatmap displays a matrix such as correlations or a pivot table.

Ask: What is one row? Which variable is compared? Is there a natural order? What comparison should be easiest to see? Monthly revenue by month is temporal and suits a line chart. Revenue by region is categorical and suits a sorted bar chart. Revenue against advertising spend is a relationship between two numeric variables and suits a scatter plot.

Avoid pie charts when readers must compare many similar slices. Avoid 3-D effects because perspective distorts apparent size. Dual axes can manufacture apparent relationships when the scales differ. A title should describe the measure and population, not merely say “Results”.

## 2. Worked example
Run this in VS Code. Install the required libraries if they are not already available: `python -m pip install pandas matplotlib seaborn`.

```python
import matplotlib.pyplot as plt

regions = ["North", "South", "East", "West"]
revenue = [185000, 142000, 98000, 121000]
ordered = sorted(zip(revenue, regions))
values, labels = zip(*ordered)

fig, ax = plt.subplots()
ax.barh(labels, values)
ax.set(title="Revenue by region", xlabel="Revenue (currency units)")
plt.show()
```

## 3. Interpreting the output
Describe the variables and units shown. Separate what the data visibly demonstrates from your explanation of why it happened. Check whether the axes, ordering, missing values and sample size could change the interpretation. A visual pattern is a clue for further analysis, not a substitute for checking the data.

## 4. Guided practice
Choose charts for: (1) score distribution, (2) daily website visits over time, (3) study hours against scores, and (4) employee counts by department. For each, state chart, axes, units and one chart type you would avoid.

## 5. Independent practice
Use a dataset with at least two meaningful variables. Write the analytical question before plotting. Inspect data types and missing values, make a chart, and write a short interpretation with one limitation and one follow-up question.

## 6. Knowledge check
1. Which data types are involved?
2. What question does this chart or technique answer?
3. What would make the result misleading?
4. What additional evidence would strengthen your interpretation?

## Lesson summary
A good visualisation makes the intended comparison easy, labels its scales and units, and does not imply more certainty than the data supports.