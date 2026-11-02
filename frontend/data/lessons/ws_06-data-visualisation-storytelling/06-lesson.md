# Lesson 6: Exploratory Visualisation with Seaborn

## Learning outcomes
By the end of this lesson, you should be able to explain the central ideas, select an appropriate method, implement it in Python, interpret the output and identify limitations.

## 1. Concepts and reasoning
Seaborn builds statistical graphics on Matplotlib and works naturally with tidy DataFrames: one observation per row and one variable per column. Common functions include histplot for distributions, boxplot for group distributions, scatterplot for relationships and pairplot for several numeric pairs.

Variables can be mapped to x, y, hue, style and size. Each additional mapping adds information but also cognitive load. Begin with one question and add another encoding only when it helps answer that question. A scatter plot may reveal curvature, clusters or an extreme point; inspect the underlying records before deciding whether that point is an error or a valid rare case.

Exploration is iterative: plot, notice, investigate and plot again. A fitted line describes an association under its assumptions; it does not prove causation. Consider confounding variables, sampling and data quality before explaining a pattern.

## 2. Worked example
Run this in VS Code. Install the required libraries if they are not already available: `python -m pip install pandas matplotlib seaborn`.

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.DataFrame({
    "study_hours": [1, 2, 2, 3, 4, 5, 6, 7],
    "score": [42, 48, 51, 55, 63, 68, 74, 78],
    "group": ["A", "A", "B", "A", "B", "B", "A", "B"]
})
sns.scatterplot(data=df, x="study_hours", y="score", hue="group")
plt.title("Study time and assessment score")
plt.show()
```

## 3. Interpreting the output
Describe the variables and units shown. Separate what the data visibly demonstrates from your explanation of why it happened. Check whether the axes, ordering, missing values and sample size could change the interpretation. A visual pattern is a clue for further analysis, not a substitute for checking the data.

## 4. Guided practice
Add a regression trend line. Compare groups A and B cautiously. Name at least three other variables (for example, prior knowledge, attendance or assessment difficulty) that could influence scores. Explain why the plot cannot establish that study hours caused higher scores.

## 5. Independent practice
Use a dataset with at least two meaningful variables. Write the analytical question before plotting. Inspect data types and missing values, make a chart, and write a short interpretation with one limitation and one follow-up question.

## 6. Knowledge check
1. Which data types are involved?
2. What question does this chart or technique answer?
3. What would make the result misleading?
4. What additional evidence would strengthen your interpretation?

## Lesson summary
A good visualisation makes the intended comparison easy, labels its scales and units, and does not imply more certainty than the data supports.