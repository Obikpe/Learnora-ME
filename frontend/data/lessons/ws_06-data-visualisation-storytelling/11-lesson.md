# Lesson 11: Categorical Comparisons and Composition

## Learning outcomes

By the end of this lesson, you should be able to compare categories with sorted, grouped and stacked charts; distinguish counts from rates and proportions; choose an appropriate category order; and explain denominator and category-overlap issues.

## 1. Core explanation
Categorical comparisons ask how groups differ. A sorted horizontal bar chart works well with long category labels. Grouped bars compare a small number of series across categories. Stacked bars show totals and composition, but internal segments are difficult to compare unless they share a baseline. A 100% stacked bar compares proportions rather than totals.

Decide whether the audience needs counts, rates or shares. If group sizes differ, counts may mislead. If the question is composition, show the denominator and explain whether categories are mutually exclusive. If categories overlap, percentages may sum to more than 100%.

Order categories intentionally: by value for ranking, by a natural sequence for stages, or alphabetically for lookup. Use a consistent order across panels. Avoid too many colours and labels; combine rare categories only when analytically defensible and disclose the grouping.

## 2. Worked Python example
Run in VS Code. Install required packages with `python -m pip install pandas numpy matplotlib seaborn plotly`.

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.DataFrame({"channel": ["Search", "Referral", "Social", "Email"],
                   "customers": [420, 180, 260, 140]}).sort_values("customers")
fig, ax = plt.subplots()
ax.barh(df.channel, df.customers)
ax.set(title="New customers by acquisition channel", xlabel="Customers", ylabel="Channel")
plt.show()
```

## 3. Interpretation and design checks
State the analytical question, population, variables, units and denominator. Check missingness and sample size. Distinguish observations from explanations and recommendations. Design for the actual audience and the size at which the visual will be viewed.

## 4. Guided practice
Create a grouped chart comparing customer counts and conversion rates by channel. Explain why the two measures should not share one numerical axis. Decide which chart best answers a composition question.

## 5. Independent practice
Apply the lesson to a dataset. Create a chart or artefact, write a caption that states the main message and caveat, and ask another person to interpret it without your explanation.

## 6. Knowledge check
1. What question does this visual answer?
2. Which encoding or design choice supports the comparison?
3. What could mislead the audience?
4. What uncertainty or limitation must be disclosed?

## Lesson summary
Effective visual communication combines accurate encoding, clear context, audience-aware design and honest interpretation.