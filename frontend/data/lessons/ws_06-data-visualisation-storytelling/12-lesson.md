# Lesson 12: Visualising Missing Data and Data Quality

## Learning outcomes

By the end of this lesson, you should be able to quantify and visualise missingness; compare missing rates across fields and groups; distinguish missing values from true zeros; explain MCAR, MAR and MNAR conceptually; and propose data-quality investigations.

## 1. Core explanation
Missingness is information about the dataset and its collection process. A blank may mean not measured, not applicable, refused, unavailable or lost during processing. These meanings are not interchangeable. Count missing values by column and check whether missingness differs across groups or time.

A missingness heatmap can show whether fields are absent together. Bar charts of missing counts are easier to read with many columns. Show the denominator or percentage missing because columns may have different row counts.

MCAR means missing completely at random; MAR means missingness is explained by observed variables; MNAR means missingness depends on the unobserved value itself. A plot cannot prove which mechanism applies. Use domain knowledge and investigate collection. Do not replace every missing value with zero: zero is a real measurement, not a universal missing code.

## 2. Worked Python example
Run in VS Code. Install required packages with `python -m pip install pandas numpy matplotlib seaborn plotly`.

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.DataFrame({"age": [21, None, 25, 30, None, 27],
                   "score": [70, 65, None, 81, 74, None],
                   "group": ["A", "A", "B", "B", "A", "B"]})
missing_pct = df.isna().mean().mul(100).sort_values()
missing_pct.plot(kind="barh")
plt.xlabel("Missing records (%)")
plt.title("Missingness by field")
plt.show()
```

## 3. Interpretation and design checks
State the analytical question, population, variables, units and denominator. Check missingness and sample size. Distinguish observations from explanations and recommendations. Design for the actual audience and the size at which the visual will be viewed.

## 4. Guided practice
Calculate missing percentages by group. If score is more often missing in one group, explain how this could bias comparisons. Propose a data-collection follow-up before choosing imputation.

## 5. Independent practice
Apply the lesson to a dataset. Create a chart or artefact, write a caption that states the main message and caveat, and ask another person to interpret it without your explanation.

## 6. Knowledge check
1. What question does this visual answer?
2. Which encoding or design choice supports the comparison?
3. What could mislead the audience?
4. What uncertainty or limitation must be disclosed?

## Lesson summary
Effective visual communication combines accurate encoding, clear context, audience-aware design and honest interpretation.