# Lesson 14: Pairwise Exploration and Faceted Visualisation

## Learning outcomes
You should be able to use `pairplot()` and `jointplot()`; explain PairGrid, JointGrid and FacetGrid; create small multiples; select variables for pairwise exploration; and avoid unreadable grids or misleading scale comparisons.

## 1. Why use multiple panels?
A dataset may contain many variables. A grid of charts can reveal relationships across variable pairs or compare the same measure across groups. Such a grid is useful for exploration, but a large grid is rarely the best final chart for a general audience.

## 2. pairplot(): pairwise relationships
A pairplot creates a matrix of charts. Off-diagonal panels show relationships between pairs of numerical variables. Diagonal panels show each variable's distribution.

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.DataFrame({
    "study_hours": [1, 2, 3, 4, 5, 6, 7, 2, 4, 6],
    "attendance": [55, 60, 65, 72, 80, 88, 92, 62, 75, 85],
    "score": [42, 48, 55, 61, 68, 75, 84, 52, 66, 78],
    "class": ["A"] * 7 + ["B"] * 3
})
grid = sns.pairplot(data=df,
                    vars=["study_hours", "attendance", "score"],
                    hue="class", diag_kind="hist", corner=True)
grid.fig.suptitle("Pairwise relationships", y=1.02)
plt.show()
```

Arguments:
- `data`: DataFrame.
- `vars`: numerical columns to include.
- `hue`: optional group variable mapped to colour.
- `diag_kind`: diagonal distribution chart, commonly histogram or KDE.
- `kind`: off-diagonal chart type, commonly scatter or KDE.
- `corner=True`: show one triangle and avoid duplicated symmetric panels.
- `plot_kws`, `diag_kws`: dictionaries of arguments passed to the corresponding plots.

Do not include every numerical column automatically. Many variables create a huge grid, and the viewer may struggle to find the important relationships.

## 3. jointplot(): one relationship with marginal distributions
A joint plot focuses on two variables. The central panel shows their relationship; the top and side panels show each variable's separate distribution.

```python
grid = sns.jointplot(data=df, x="study_hours", y="score",
                     kind="scatter", height=6,
                     marginal_kws={"bins": 8})
plt.show()
```

Use this when you want to inspect one pair and both marginal distributions. The `kind` argument can select supported alternatives such as scatter, KDE, hexbin or regression-style views. It manages its own figure, so it is figure-level.

## 4. FacetGrid: one panel per group
Faceting creates small multiples. Each panel displays a subset of the data:

```python
grid = sns.FacetGrid(df, col="class", height=4,
                     sharex=True, sharey=True)
grid.map_dataframe(sns.scatterplot,
                   x="study_hours", y="score")
grid.set_axis_labels("Study hours", "Score")
grid.set_titles("Class {col_name}")
plt.show()
```

- `col` creates columns of panels; `row` creates rows.
- `height` controls panel height.
- `sharex` and `sharey` determine whether panels share scales.
- `map_dataframe()` passes each panel's subset of the DataFrame to the plotting function.

Shared axes support direct comparisons. Independent axes can reveal within-group patterns but can make very different ranges look similar. Choose according to the question.

## 5. PairGrid for custom combinations
PairGrid gives more control over the diagonal and two triangles:

```python
grid = sns.PairGrid(df, vars=["study_hours", "attendance", "score"])
grid.map_lower(sns.scatterplot, alpha=0.7)
grid.map_diag(sns.histplot)
grid.map_upper(sns.regplot, scatter_kws={"alpha": 0.5})
plt.show()
```

- `map_lower()` draws in the lower triangle.
- `map_upper()` draws in the upper triangle.
- `map_diag()` draws on the diagonal.

This is useful when scatter plots are appropriate below the diagonal but a different view is useful above it.

## 6. relplot() and catplot()
For common tasks, figure-level functions are easier:
```python
sns.relplot(data=df, x="study_hours", y="score",
            hue="class", col="class", kind="scatter",
            height=4, aspect=1)
plt.show()
```
For categorical facets, `sns.catplot()` provides a figure-level interface for strip, swarm, box, violin, point, bar and count plots. It is preferable to manually creating every panel when the same chart is repeated across groups.

## 7. Common mistakes
- Including too many variables.
- Using too many hue categories.
- Forgetting that pairplots repeat symmetric relationships.
- Comparing facets with independent scales as if they were shared.
- Treating KDE contours as observed records.
- Presenting a huge exploratory grid as the final report.

## Guided practice
1. Create a pairplot for three numerical variables.
2. Add a hue group and set `corner=True`.
3. Create a jointplot and inspect its marginal distributions.
4. Create a FacetGrid with shared axes.
5. Change to independent y-scales and explain the visual difference.

## Independent practice
Use at least three numerical variables and one categorical variable. Create a pairplot and a faceted chart. Identify two relationships worth investigating, then create focused charts suitable for a report. Explain why the full grid is exploratory.

## Knowledge check
1. What appears on the diagonal of a pairplot?
2. What are marginal distributions?
3. What is a facet?
4. What does `sharey=True` do?
5. Why can independent facet scales mislead comparisons?

## Lesson summary
Pairwise and faceted plots support exploration across variables and groups. Use `pairplot()` for a relationship matrix, `jointplot()` for one relationship with marginal distributions, and grid objects for custom small multiples. Turn exploratory patterns into focused charts before presenting them.