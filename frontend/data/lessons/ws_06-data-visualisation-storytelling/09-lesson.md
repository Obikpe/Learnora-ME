# Lesson 9: Multivariate Visualisation

## Learning outcomes
Explain the visualisation method, implement the worked example in Python, interpret it and communicate its limitations.

## 1. Core explanation
Multivariate analysis examines three or more variables. A scatter plot can use hue, marker shape or size for additional fields, but each encoding increases complexity. A pair plot displays pairwise relationships among numeric variables and can reveal clusters or redundant features. A correlation heatmap summarises linear associations, not causal links.

The goal is not to encode every column in one graphic. Choose a question and select the few variables needed to answer it. Faceting creates separate small charts for groups and often improves readability. Standardise scales when comparing panels, but do not standardise away meaningful differences without explanation.

Simpson's paradox can occur when a trend within each subgroup reverses when groups are combined because group sizes or baseline rates differ. If an overall relationship seems surprising, colour or facet by a plausible grouping variable and inspect subgroup patterns.

## 2. Worked Python example
Run in VS Code. Install required packages with `python -m pip install pandas numpy matplotlib seaborn plotly`.

```python
import seaborn as sns
import matplotlib.pyplot as plt

penguins = sns.load_dataset("penguins").dropna()
sns.pairplot(penguins, vars=["bill_length_mm", "bill_depth_mm", "flipper_length_mm"],
             hue="species", corner=True)
plt.show()
```

## 3. Interpretation and design checks
State the analytical question, population, variables, units and denominator. Check missingness and sample size. Distinguish observations from explanations and recommendations. Design for the actual audience and the size at which the visual will be viewed.

## 4. Guided practice
Inspect the penguins dataset. Identify one pair of variables that separates species visually and one pair that overlaps. Explain why a visual cluster is not automatically a reliable classifier.

## 5. Independent practice
Apply the lesson to a dataset. Create a chart or artefact, write a caption that states the main message and caveat, and ask another person to interpret it without your explanation.

## 6. Knowledge check
1. What question does this visual answer?
2. Which encoding or design choice supports the comparison?
3. What could mislead the audience?
4. What uncertainty or limitation must be disclosed?

## Lesson summary
Effective visual communication combines accurate encoding, clear context, audience-aware design and honest interpretation.