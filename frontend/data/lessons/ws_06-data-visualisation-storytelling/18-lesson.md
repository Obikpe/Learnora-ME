# Lesson 18: Multi-Chart Figures and Dashboard Layouts

## Learning outcomes
You should be able to create multiple Matplotlib Axes with `subplots()`; control rows, columns and shared axes; add Seaborn charts to selected panels; design consistent scales and labels; organise a dashboard around decisions; and export a multi-panel figure.

## 1. Why combine charts?
A single chart rarely answers every question. A report may need a trend, category comparison and distribution. A multi-panel figure places related charts together. Each panel should have a distinct purpose; do not add charts merely to fill space.

## 2. Create a grid with plt.subplots()
```python
import matplotlib.pyplot as plt
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 7))
```

- `nrows`: number of rows.
- `ncols`: number of columns.
- `figsize`: overall Figure dimensions.
- `axes`: array of Axes objects when there is more than one panel.

For a 2-by-2 grid, address panels as `axes[0, 0]`, `axes[0, 1]`, `axes[1, 0]` and `axes[1, 1]`. Indexing begins at zero.

## 3. Draw different charts in one Figure
```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.DataFrame({
    "month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    "orders": [42, 51, 47, 63, 66, 72],
    "region": ["North", "South", "North", "South", "North", "South"],
    "score": [60, 65, 62, 70, 72, 75]
})

fig, axes = plt.subplots(2, 2, figsize=(11, 8),
                         layout="constrained")
axes[0, 0].plot(df["month"], df["orders"], marker="o")
axes[0, 0].set_title("Orders over time")
axes[0, 0].set_ylabel("Orders")

sns.barplot(data=df, x="region", y="orders",
            estimator="sum", errorbar=None, ax=axes[0, 1])
axes[0, 1].set_title("Total orders by region")
axes[0, 1].set_ylabel("Orders")

sns.histplot(data=df, x="score", bins=5, ax=axes[1, 0])
axes[1, 0].set_title("Score distribution")

axes[1, 1].scatter(df["orders"], df["score"])
axes[1, 1].set_title("Orders and score")
axes[1, 1].set_xlabel("Orders")
axes[1, 1].set_ylabel("Score")

fig.suptitle("Operational overview", fontsize=16)
plt.show()
```

This is a layout demonstration, not strong statistical evidence: the dataset is tiny. In real work, confirm the unit of observation and sample size support each comparison.

## 4. Shared axes
`sharex=True` or `sharey=True` gives panels common axis limits. This is useful when the same measure should be compared directly. Independent scales can reveal within-group patterns but may make very different ranges look similar. Choose deliberately.

## 5. Layout controls
- `layout="constrained"` asks Matplotlib to arrange spacing.
- `fig.tight_layout()` adjusts subplot spacing.
- `fig.suptitle()` adds a Figure-wide title.
- `ax.set_title()` titles an individual panel.
- `fig.savefig()` exports the complete Figure.

Use panel titles to state each chart's question. The overall title explains the shared subject.

## 6. A dashboard is not just a grid
A dashboard is a coordinated view for recurring monitoring or decision support. Design it around:
1. Who uses it?
2. What decision must they make?
3. Which measures are necessary?
4. What time period and filters apply?
5. How often does data refresh?
6. What should happen when a measure crosses a threshold?

A dashboard may contain KPI cards, a trend, group breakdowns, a detailed table and visible filters. A KPI needs context: current value, comparison period, target, denominator and direction where relevant.

## 7. Hierarchy and consistency
Put the most important decision information first. Use consistent colours for the same group. Keep units, date filters and definitions consistent. Avoid unexplained red/green status, excessive gauges and tiny text. Show the refresh time and data coverage.

Filters should not silently change denominators. If a user selects one region, make clear that the displayed totals now refer only to that region.

## 8. Export and test
```python
fig.savefig("operational_overview.png", dpi=200,
            bbox_inches="tight")
fig.savefig("operational_overview.pdf", bbox_inches="tight")
```

Open the saved file at the intended size. Check labels, panel alignment and legends. Ask someone to answer the dashboard's main question without your explanation.

## Common mistakes
- Too many panels.
- Different scales for charts that should be compared.
- Repeating the same information.
- Omitting period or refresh time.
- KPI cards without context or denominator.
- Hiding filter effects.
- Exporting without inspecting the saved file.

## Guided practice
1. Create a 2-by-2 grid.
2. Draw four chart types on the axes.
3. Share scales where appropriate.
4. Add an overall title and panel titles.
5. Export and inspect the figure.

## Independent practice
Sketch a dashboard for a training manager with no more than five views. For each, state its question, measure, unit, denominator, period and supported decision. Implement four views in a multi-panel figure.

## Knowledge check
1. What does `plt.subplots(2, 2)` return?
2. Why use shared axes?
3. Difference between panel and Figure title?
4. What context should a KPI include?
5. Why show refresh time?

## Lesson summary
Multi-panel figures connect evidence. `subplots()` creates the grid, and Seaborn can draw into selected Matplotlib Axes. A dashboard must be organised around decisions, consistent definitions and readable context—not simply a collection of charts.