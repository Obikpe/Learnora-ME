# Lesson 8: Relationships and Bivariate Analysis

## Learning outcomes

By the end of this lesson, you should be able to inspect relationships between two numeric variables; distinguish Pearson correlation from Spearman correlation; choose scatter, regression or grouped-distribution plots; identify outliers and subgroup effects; and explain why association does not establish causation.

## 1. Core explanation
Bivariate analysis studies how two variables vary together. For two numeric variables, a scatter plot shows direction, form, strength and unusual points. Pearson correlation measures linear association and ranges from -1 to +1. A value near zero does not rule out a curved relationship. Spearman correlation uses ranks and can detect monotonic relationships that are not linear.

For a numeric variable across categories, compare distributions with box plots rather than only group means. For two categorical variables, use a contingency table and grouped or stacked bars. Check sample sizes: a proportion based on a handful of records is uncertain.

Correlation is not causation. A third variable may influence both, direction may be reversed, or the relationship may be coincidental. Outliers can strongly affect correlation. Plot the data before trusting a coefficient and consider whether the relationship is linear, monotonic or driven by a subgroup.

## 2. Worked Python example
Run in VS Code. Install required packages with `python -m pip install pandas numpy matplotlib seaborn plotly`.

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.DataFrame({"study_hours": [1,2,3,4,5,6,7,8],
                   "score": [45,50,54,62,65,70,74,78]})
print(df.corr(numeric_only=True))
sns.regplot(data=df, x="study_hours", y="score")
plt.title("Study hours and assessment score")
plt.show()
```

## 3. Interpretation and design checks
State the analytical question, population, variables, units and denominator. Check missingness and sample size. Distinguish observations from explanations and recommendations. Design for the actual audience and the size at which the visual will be viewed.

## 4. Guided practice
Add an observation with unusually high study hours but a low score. Recalculate correlation and compare the plot. Explain why outlier investigation should precede automatic deletion.

## 5. Independent practice
Apply the lesson to a dataset. Create a chart or artefact, write a caption that states the main message and caveat, and ask another person to interpret it without your explanation.

## 6. Knowledge check
1. What question does this visual answer?
2. Which encoding or design choice supports the comparison?
3. What could mislead the audience?
4. What uncertainty or limitation must be disclosed?

## Lesson summary
Effective visual communication combines accurate encoding, clear context, audience-aware design and honest interpretation.