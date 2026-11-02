# Lesson 5: Matplotlib Scatter Plots and Relationships

## Learning outcomes
You should be able to decide when a scatter plot is suitable; create one with `ax.scatter()`; map variables to x, y, colour and marker size; control transparency and marker appearance; handle overplotting; add trend lines; and explain why association is not causation.

## 1. What question does a scatter plot answer?

A scatter plot displays the relationship between two numerical variables. Each point represents one observation, with its horizontal position determined by one variable and its vertical position determined by another.

Examples:
- Study hours against examination score.
- Advertising spend against sales.
- Customer age against monthly spending.
- Temperature against electricity demand.

A scatter plot helps you see direction, form, strength, clusters and unusual observations. It does not automatically tell you why a relationship exists.

Use a scatter plot when both variables are numerical and individual paired observations matter. Do not use it to compare category totals; use a bar chart. If x is time and the sequence is important, a line chart may be more appropriate.

## 2. The ax.scatter() function

The general pattern is:

```python
ax.scatter(x, y, s=None, c=None, marker="o",
           alpha=None, cmap=None, edgecolors=None)
```

- `x`: numerical horizontal values.
- `y`: numerical vertical values.
- `s`: marker area in points squared. A larger number creates a larger marker.
- `c`: one colour or values mapped to a colour scale.
- `marker`: marker shape, such as `"o"`, `"s"` or `"^`.
- `alpha`: transparency from 0 to 1.
- `cmap`: colour map used when `c` contains numerical values.
- `edgecolors`: marker border colour.

The x and y arrays must have matching lengths. If you have 30 learners, you need 30 study-hour values and 30 corresponding scores.

## 3. Your first scatter plot

```python
import matplotlib.pyplot as plt

study_hours = [1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7]
scores =      [42, 48, 51, 55, 58, 61, 65, 67, 72, 75, 78, 84]

fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(study_hours, scores, s=65, color="royalblue",
           alpha=0.8, edgecolors="black")
ax.set(title="Study hours and examination score",
       xlabel="Study hours per week", ylabel="Score (out of 100)")
ax.set_xlim(0, 8)
ax.set_ylim(0, 100)
ax.grid(alpha=0.2)
plt.show()
```

Each dot is one learner. The pattern rises from left to right, suggesting a positive association in this small example. It does not prove that increasing study time alone causes a higher score. Prior knowledge, attendance, support and other factors may also matter.

## 4. Add a third variable using colour

You can use colour to represent another numerical variable. For example, suppose each learner also has an attendance percentage:

```python
import matplotlib.pyplot as plt

hours = [1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7]
scores = [42, 48, 51, 55, 58, 61, 65, 67, 72, 75, 78, 84]
attendance = [55, 60, 65, 70, 75, 78, 80, 82, 85, 88, 92, 95]

fig, ax = plt.subplots(figsize=(7, 5))
points = ax.scatter(hours, scores, c=attendance, cmap="viridis",
                    s=80, edgecolors="black")
fig.colorbar(points, ax=ax, label="Attendance (%)")
ax.set(title="Study hours, score and attendance",
       xlabel="Study hours per week", ylabel="Score")
plt.show()
```

Here, `c=attendance` maps the attendance values to colours. `cmap="viridis"` chooses a sequential colour map. `fig.colorbar()` adds a key that explains which colours correspond to which attendance values. Without a colour bar, the viewer cannot decode the scale.

Use sequential colour maps for ordered numeric quantities. For unrelated categories, use distinct categorical colours instead. Avoid a rainbow palette for numerical magnitude because its colour changes can imply artificial boundaries.

## 5. Map a fourth variable to marker size

Marker size can represent another quantity:

```python
revenue = [20, 30, 25, 45, 50, 55, 60, 70, 65, 80, 90, 100]
fig, ax = plt.subplots(figsize=(7, 5))
points = ax.scatter(hours, scores, s=[v * 2 for v in revenue],
                    c=attendance, cmap="viridis", alpha=0.7)
fig.colorbar(points, ax=ax, label="Attendance (%)")
ax.set(title="Study hours, score, attendance and revenue-sized markers",
       xlabel="Study hours", ylabel="Score")
plt.show()
```

This is a teaching example of bubble encoding. In real analysis, avoid putting too many variables into one chart. Human readers have difficulty accurately comparing circle areas. If size is used, explain what it represents and consider a separate panel.

## 6. Overplotting and transparency

When many observations share similar coordinates, points overlap. The chart may look like one solid blob even though many records exist. This is called **overplotting**.

Possible solutions:
- Reduce marker size.
- Use transparency with `alpha=0.2` or similar.
- Sample points for exploration, while clearly disclosing sampling.
- Use a hexbin or 2-D density view for very large datasets.
- Add jitter only for discrete-valued variables and explain that jitter is a display adjustment, not real data.

A transparent cloud can reveal dense regions because overlapping points become darker. Transparency is not a complete solution when the dataset is extremely large.

## 7. Add a fitted straight line

A simple linear trend can summarise the average direction:

```python
import numpy as np
import matplotlib.pyplot as plt

x = np.array([1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7])
y = np.array([42, 48, 51, 55, 58, 61, 65, 67, 72, 75, 78, 84])

slope, intercept = np.polyfit(x, y, 1)
predicted = slope * x + intercept

fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(x, y, label="Observed learners")
ax.plot(x, predicted, color="darkred", label="Linear fit")
ax.set(xlabel="Study hours", ylabel="Score",
       title="Observed scores and a fitted linear trend")
ax.legend()
plt.show()
print("Slope:", slope)
```

`np.polyfit(x, y, 1)` fits a straight line using a least-squares method. The number 1 means a first-degree polynomial (a straight line). The returned slope describes the estimated change in y for a one-unit increase in x under this fitted linear model. It is not automatically a causal effect.

## 8. Correlation is not causation

A positive scatter pattern means higher x values tend to appear with higher y values in the observed data. It does not establish that changing x will change y. Confounding variables, selection effects, reverse direction and coincidence can produce associations.

A scatter plot is a diagnostic and exploratory tool. Before making a causal statement, consider study design, temporal order, confounders, sampling and alternative explanations.

## 9. Common mistakes

- Using scatter plots for category counts.
- Forgetting units on axes.
- Mapping a third variable to colour without a colour bar.
- Using marker area without explaining what size means.
- Treating the fitted line as proof of causation.
- Ignoring outliers that strongly affect the fitted line.
- Hiding dense observations through excessive opacity or overplotting.

## Guided practice

1. Create the first scatter plot and identify each observation.
2. Change marker size and transparency.
3. Add attendance as colour and include a colour bar.
4. Fit a straight line and interpret its slope in context.
5. Describe one possible confounder that could explain the relationship.

## Independent practice

Find or create a dataset with at least 30 paired numerical observations. Make a scatter plot, label both axes with units, inspect clusters and outliers, and calculate a correlation coefficient. Explain why correlation does not prove causation and state what additional evidence would be needed for a causal conclusion.

## Knowledge check

1. What does one point represent?
2. What does the `s` argument control?
3. Why should a numerical colour mapping include a colour bar?
4. What is overplotting?
5. Why is a fitted trend line not proof of causation?

## Lesson summary

Scatter plots reveal relationships between numerical variables. Matplotlib's `ax.scatter()` lets you encode additional variables through colour and size, but extra encodings increase cognitive load. Use transparency and density methods for crowded data, label units and interpret association carefully.