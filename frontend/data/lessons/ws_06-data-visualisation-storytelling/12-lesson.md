# Lesson 12: Seaborn Relational Visualisation

## Learning outcomes
You should be able to use `scatterplot()`, `lineplot()` and `relplot()`; map variables to hue, size and style; understand aggregation and uncertainty in line plots; use facets to compare groups; and avoid misleading relational charts.

## 1. What is relational visualisation?

Relational charts show how one or more variables relate. Scatter plots display individual paired observations. Line plots show ordered x values, often time, and may aggregate repeated observations. Seaborn makes these charts easier to build from DataFrames.

Choose:
- Scatter plot for individual pairs of numerical values.
- Line plot for an ordered x variable, especially time.
- Faceted relational plot when one panel per group makes comparisons clearer.

## 2. scatterplot(): individual relationships

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.DataFrame({
    "hours": [1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7],
    "score": [42, 48, 51, 55, 58, 61, 65, 67, 72, 75, 78, 84],
    "class": ["A"] * 6 + ["B"] * 6,
    "attendance": [55, 60, 65, 70, 75, 78, 80, 82, 85, 88, 92, 95]
})

fig, ax = plt.subplots(figsize=(8, 5))
sns.scatterplot(data=df, x="hours", y="score",
                hue="class", style="class", size="attendance",
                sizes=(50, 180), alpha=0.8, ax=ax)
ax.set(title="Study hours and score",
       xlabel="Study hours per week", ylabel="Score")
plt.show()
```

Important arguments:
- `x`, `y`: numerical variables.
- `hue`: variable mapped to colour.
- `style`: variable mapped to marker style.
- `size`: variable mapped to marker size.
- `sizes`: minimum and maximum marker sizes when size is mapped.
- `alpha`: transparency.
- `palette`: colour mapping.
- `legend`: whether to display a legend.

The chart encodes four fields, but that can be too much. Always inspect whether the legend remains readable and whether the audience can decode each mapping.

## 3. lineplot(): ordered relationship and aggregation

A Seaborn line plot is often used for time series. Unlike a simple Matplotlib line, Seaborn can aggregate repeated y observations at each x value and show an uncertainty interval.

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.DataFrame({
    "week": [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4],
    "class": ["A", "B", "C"] * 4,
    "score": [60, 65, 58, 62, 67, 61, 66, 70, 64, 68, 73, 67]
})

fig, ax = plt.subplots(figsize=(8, 5))
sns.lineplot(data=df, x="week", y="score",
             hue="class", marker="o", estimator="mean",
             errorbar=("ci", 95), ax=ax)
ax.set(title="Average score by week and class",
       xlabel="Week", ylabel="Mean score")
plt.show()
```

If multiple observations share the same x value and group, Seaborn can estimate a summary (mean by default). `estimator="mean"` makes this explicit. `errorbar=("ci", 95)` requests a 95% confidence interval for the estimate using Seaborn's supported procedure. It is not the range containing 95% of individual learners.

If you want to show every raw observation without aggregation, set `estimator=None` when appropriate, or use a scatter plot. Do not let automatic aggregation hide the number or variability of observations.

## 4. Important lineplot arguments

- `data`: source DataFrame.
- `x`, `y`: variables.
- `hue`: separate lines by colour.
- `style`: separate line styles or markers.
- `size`: map a variable to line width.
- `estimator`: summary function for repeated x values; commonly mean, or `None` to avoid aggregation.
- `errorbar`: interval or variability display.
- `sort`: whether x values are sorted before connecting.
- `markers`: whether to show markers.
- `dashes`: whether to vary line dashes.
- `legend`: legend behaviour.

For a time series, ensure x is parsed as a date or a properly ordered numerical value. Do not connect unrelated nominal categories.

## 5. relplot(): figure-level relational charts

`relplot()` is figure-level and can create small multiples:

```python
grid = sns.relplot(
    data=df,
    x="week", y="score",
    hue="class",
    kind="line",
    marker="o",
    col="class",
    height=4,
    aspect=1.0
)
grid.set_axis_labels("Week", "Score")
grid.set_titles("Class {col_name}")
plt.show()
```

The `kind` argument chooses the relational chart type, such as `"scatter"` or `"line"`. `col` creates columns of panels; `row` can create rows. `height` and `aspect` control panel size. Because relplot manages the full Figure, it does not take a normal `ax=` argument.

Facets reduce overlap and make group patterns easier to compare, but use common axis limits when direct comparison is intended. Independent scales can make small changes look equally large across panels.

## 6. When to use scatter versus line

Use scatter when each dot is a separate paired observation and the x values are not a continuous sequence that should be connected. Use line when the x variable is ordered and connecting successive values helps the viewer understand change.

If x is time and there are multiple measurements per date, decide whether to show individual points, a mean or another summary. State the aggregation clearly.

## 7. Common mistakes

- Connecting unrelated categories with lines.
- Forgetting that Seaborn lineplot may aggregate repeated x values.
- Interpreting confidence intervals as the range of individual observations.
- Using too many hue categories.
- Mapping size to a variable without a clear legend.
- Comparing facets with different scales without disclosing it.

## Guided practice

1. Build a scatter plot with hue and style.
2. Add a numerical size mapping and explain the legend.
3. Create a line plot with repeated observations per week.
4. Compare `estimator="mean"` with `estimator=None`.
5. Create a faceted `relplot()` and compare group patterns.

## Independent practice

Use a dataset with an ordered variable, a numerical response and at least one group. Create a scatter or line plot and a faceted version. Explain the aggregation choice, uncertainty display, axis scales and limitations.

## Knowledge check

1. What is the difference between scatterplot and lineplot?
2. What does `estimator` do in lineplot?
3. What does `errorbar=("ci", 95)` communicate?
4. What is a facet?
5. Why might independent facet scales mislead comparisons?

## Lesson summary

Seaborn relational charts make it convenient to map multiple variables to colour, marker, size and panels. Scatter plots preserve individual pairs; line plots often aggregate repeated x values; relplot creates figure-level facets. Understand these behaviours before interpreting the chart.