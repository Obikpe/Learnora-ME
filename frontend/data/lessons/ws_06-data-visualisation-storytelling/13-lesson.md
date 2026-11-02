# Lesson 13: Heatmaps, Correlation and Matrix Visualisation

## Learning outcomes
You should be able to build a pivot table; explain what each cell represents; calculate and visualise correlations; use Seaborn's `heatmap()`; customise annotations, colour maps, limits and masks; and explain why correlation does not prove causation.

## 1. What is a heatmap?
A heatmap represents values in a rectangular matrix using colour. Each cell represents the combination of one row category and one column category. Examples include revenue by region and month, attendance by weekday and hour, and correlations between numerical variables.

A heatmap works when both dimensions have meaningful categories and cell values share a comparable scale. Too many rows or columns make labels unreadable. A colour bar is essential because it explains what the colours mean.

## 2. Create a pivot table
Suppose each row is a sales transaction. We want total revenue by region and month.

```python
import pandas as pd
sales = pd.DataFrame({
    "region": ["North", "North", "South", "South", "East", "East"],
    "month": ["Jan", "Feb", "Jan", "Feb", "Jan", "Feb"],
    "revenue": [120, 140, 90, 110, 100, 130]
})
matrix = sales.pivot(index="region", columns="month", values="revenue")
print(matrix)
```

`index` determines the matrix rows; `columns` determines its columns; `values` supplies the cell values. If more than one record exists per region-month pair, use `pivot_table()` with an aggregation:

```python
matrix = sales.pivot_table(index="region", columns="month",
                           values="revenue", aggfunc="sum")
```

The aggregation changes the question: `sum` means total revenue, `mean` means average transaction revenue, and `count` means number of records. State which you use.

## 3. Seaborn heatmap()

```python
import seaborn as sns
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(7, 4))
sns.heatmap(matrix, annot=True, fmt=".0f", cmap="YlGnBu",
            linewidths=0.5,
            cbar_kws={"label": "Revenue"})
ax.set_title("Revenue by region and month")
ax.set_xlabel("Month")
ax.set_ylabel("Region")
plt.show()
```

Important arguments:
- `data`: rectangular matrix or DataFrame.
- `annot=True`: print each cell's value.
- `fmt=".0f"`: format annotations as whole numbers; use `".2f"` for two decimals.
- `cmap`: colour map.
- `vmin`, `vmax`: minimum and maximum values mapped to the colour scale.
- `center`: value that should appear at the centre of a diverging palette.
- `linewidths`, `linecolor`: cell borders.
- `cbar`: show or hide the colour bar.
- `cbar_kws`: customise the colour bar.
- `mask`: hide selected cells, often one half of a symmetric matrix.

Annotations are useful for small matrices, but too many numbers create clutter.

## 4. Correlation
Correlation measures the direction and strength of a particular association between two numerical variables. Pearson correlation ranges from -1 to +1:
- +1: perfect positive linear association.
- 0: no linear association.
- -1: perfect negative linear association.

A correlation near zero does not rule out a non-linear relationship. Correlation is sensitive to outliers and does not establish causation.

```python
df = pd.DataFrame({
    "study_hours": [1, 2, 3, 4, 5, 6, 7],
    "attendance": [55, 60, 65, 72, 80, 88, 92],
    "score": [42, 48, 55, 61, 68, 75, 84]
})
corr = df.corr(numeric_only=True, method="pearson")
print(corr)
```

Pandas calculates pairwise correlations. Missing values are handled pairwise by default, so different cells may use different sample sizes. Inspect missingness and sample sizes before interpreting the matrix.

## 5. Correlation heatmap
```python
fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="vlag",
            center=0, vmin=-1, vmax=1, square=True,
            linewidths=0.5, ax=ax)
ax.set_title("Pearson correlation between learner measures")
plt.show()
```

A diverging palette is appropriate because zero is a meaningful midpoint. Fixing the scale from -1 to +1 keeps different correlation heatmaps comparable.

A correlation matrix is symmetric: correlation(A, B) equals correlation(B, A). You can hide the repeated upper triangle:

```python
import numpy as np
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f",
            cmap="vlag", center=0, vmin=-1, vmax=1)
plt.show()
```

`np.triu()` creates the upper-triangle boolean mask; True cells are hidden.

## 6. Choose the colour scale carefully
Use sequential palettes for low-to-high quantities such as counts. Use diverging palettes for values around a meaningful midpoint such as zero correlation or deviation from target. Keep limits fixed when comparing heatmaps. Do not fill missing cells with zero unless zero is genuinely the observed value.

## 7. Common mistakes
- Treating correlation as causation.
- Forgetting that pivot results depend on the aggregation.
- Comparing heatmaps with different colour limits.
- Using rainbow palettes without a meaningful ordering.
- Filling missing values with zero without justification.
- Adding annotations to a matrix too large to read.

## Guided practice
1. Create a region-by-month pivot table.
2. Change the aggregation from sum to mean.
3. Plot both matrices with annotations.
4. Calculate a correlation matrix.
5. Plot it with a fixed -1 to +1 diverging scale and mask the upper triangle.

## Independent practice
Use at least four numerical variables. Calculate and plot their correlation matrix. Then inspect selected pairs with scatter plots. Explain why a correlation value alone is not enough to conclude that one variable causes another.

## Knowledge check
1. What do the rows, columns and cells in a heatmap represent?
2. What does `annot=True` do?
3. Why is a diverging palette suitable for correlations?
4. What does Pearson correlation of zero mean—and not mean?
5. Why can missing values cause different cells to use different sample sizes?

## Lesson summary
Heatmaps make matrix patterns visible. Pivot tables require a clearly stated aggregation, and correlation heatmaps need a meaningful diverging scale. Always inspect the underlying data and avoid interpreting correlation as proof of cause.