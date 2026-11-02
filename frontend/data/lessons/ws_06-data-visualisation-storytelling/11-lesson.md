# Lesson 11: Seaborn Categorical Visualisation

## Learning outcomes
You should be able to distinguish category counts from statistical estimates; use Seaborn's `countplot()`, `barplot()`, `pointplot()`, `boxplot()`, `violinplot()`, `stripplot()` and `swarmplot()`; control category order, hue and error bars; and choose the chart that answers the question.

## 1. Categorical charts do not all show the same thing

A common source of confusion is treating every chart with categories on the x-axis as equivalent. They answer different questions:

- Count plot: how many records are in each category?
- Bar plot: what is an estimated numerical value for each category?
- Point plot: how do estimated values compare, often with intervals?
- Box plot: how are numerical observations distributed within categories?
- Violin plot: what is the smoothed distribution shape within categories?
- Strip/swarm plot: where are the individual observations?

Before plotting, decide whether you want a count, a summary estimate or the raw distribution.

## 2. Prepare a realistic dataset

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.DataFrame({
    "department": ["Sales", "Sales", "Sales", "Support", "Support",
                   "Support", "Engineering", "Engineering", "Engineering"],
    "satisfaction": [4, 5, 3, 3, 4, 4, 5, 5, 4],
    "tickets": [12, 15, 10, 18, 20, 17, 8, 9, 7]
})
sns.set_theme(style="whitegrid")
```

Each row is one observation. Department is categorical. Satisfaction is an ordinal score. Tickets is a numerical count. This small table will demonstrate the different questions.

## 3. countplot(): count observations

```python
fig, ax = plt.subplots(figsize=(7, 4))
sns.countplot(data=df, x="department",
              order=["Sales", "Support", "Engineering"], ax=ax)
ax.set(title="Number of records by department",
       xlabel="Department", ylabel="Number of records")
plt.show()
```

`countplot()` counts rows in each category. It does not calculate the average of another variable. Common arguments:
- `data`: source DataFrame.
- `x` or `y`: categorical variable.
- `hue`: split counts by another category.
- `order`: explicit category order.
- `hue_order`: explicit hue order.
- `stat`: count or proportion-style summary in supported versions.
- `dodge`: separate hue groups side by side when appropriate.

Use countplot to answer “how many observations are in each category?” If one row represents an event but you need unique customers, first aggregate to customer level or calculate the distinct count correctly. A row count is not automatically a customer count.

## 4. barplot(): estimate a numerical value by category

```python
fig, ax = plt.subplots(figsize=(7, 4))
sns.barplot(data=df, x="department", y="satisfaction",
            errorbar=("ci", 95), ax=ax)
ax.set(title="Mean satisfaction by department",
       xlabel="Department", ylabel="Mean satisfaction score")
plt.show()
```

A bar plot usually calculates an estimator (the mean by default) for each category. The bar height is not the number of records. The interval shows uncertainty around the estimate, based on the selected method.

Important arguments:
- `x`, `y`: category and numerical response.
- `estimator`: summary function; default is the mean.
- `errorbar`: interval method in current Seaborn versions; examples include confidence intervals or standard deviation.
- `n_boot`: number of bootstrap samples used for some interval calculations.
- `hue`: additional category for subgroup estimates.
- `order`: category order.
- `capsize`: cap width on error bars.

If the question is about the median, use a median estimator where supported, or show a box plot. Do not label a mean bar as “number of employees”.

## 5. pointplot(): estimates without full bars

```python
fig, ax = plt.subplots(figsize=(7, 4))
sns.pointplot(data=df, x="department", y="satisfaction",
              errorbar=("ci", 95), join=False, ax=ax)
ax.set(title="Estimated satisfaction by department",
       ylabel="Mean satisfaction")
plt.show()
```

A point plot highlights estimates and intervals without filling a full bar. It is useful when the position of the estimate matters more than a bar's area. For time or ordered categories, joining points may suggest a progression; for unrelated categories, `join=False` avoids implying continuity.

## 6. boxplot(): compare quartiles and spread

```python
fig, ax = plt.subplots(figsize=(7, 4))
sns.boxplot(data=df, x="department", y="tickets",
            showfliers=True, ax=ax)
ax.set(title="Ticket distribution by department",
       ylabel="Tickets per record")
plt.show()
```

A box plot shows median, quartiles, IQR and potential outliers. It does not show every observation. Use it when spread and outliers matter, not merely to display a mean.

## 7. violinplot(): compare distribution shapes

```python
fig, ax = plt.subplots(figsize=(7, 4))
sns.violinplot(data=df, x="department", y="tickets",
               inner="quart", cut=0, ax=ax)
ax.set(title="Ticket distributions by department",
       ylabel="Tickets")
plt.show()
```

The width shows estimated density. `inner="quart"` displays quartile information. `cut=0` prevents the estimated density from extending beyond the observed range. KDE smoothing can be unstable for small groups, so do not overinterpret a tiny dataset's violin shape.

## 8. stripplot() and swarmplot(): individual records

```python
fig, ax = plt.subplots(figsize=(7, 4))
sns.stripplot(data=df, x="department", y="tickets",
              jitter=0.12, alpha=0.7, ax=ax)
ax.set_title("Individual ticket counts by department")
plt.show()
```

A strip plot displays each observation. Jitter moves points slightly sideways to reduce exact overlap. The jitter is visual only; it does not change the measured ticket count.

```python
fig, ax = plt.subplots(figsize=(7, 4))
sns.swarmplot(data=df, x="department", y="tickets",
              size=6, ax=ax)
ax.set_title("Ticket counts with overlap-reduced points")
plt.show()
```

A swarm plot adjusts point positions to reduce overlap. It can become slow or crowded for large data.

## 9. Use hue to compare subgroups

```python
fig, ax = plt.subplots(figsize=(8, 4))
sns.barplot(data=df, x="department", y="tickets",
            hue="department", legend=False, ax=ax)
ax.set_title("Mean tickets by department")
plt.show()
```

For a useful hue comparison, choose a second variable that creates meaningful subgroups, such as year or customer type. Avoid mapping the same variable to x and hue unless you have a clear reason.

## 10. Category order matters

By default, Seaborn may use the order found in the data or a natural order for some categories. If categories have a meaningful sequence—such as beginner, intermediate, advanced—specify it:

```python
sns.countplot(data=df, x="department",
              order=["Engineering", "Sales", "Support"])
```

For nominal categories, sorting by value can help comparison. For ordinal categories, preserve the natural order rather than alphabetically sorting labels.

## 11. Choosing the correct categorical chart

| Your question | Use |
|---|---|
| How many records belong to each category? | countplot |
| What is the average or other estimate per category? | barplot |
| How do estimates and intervals compare? | pointplot |
| What are median, quartiles and potential outliers? | boxplot |
| What is the smoothed distribution shape? | violinplot |
| Where are the individual observations? | stripplot or swarmplot |

## 12. Common mistakes

- Reading a barplot as a countplot.
- Forgetting that the default barplot estimator is the mean.
- Treating confidence intervals as the full range of individual values.
- Using a violin plot with too few observations and overinterpreting its shape.
- Hiding category order.
- Counting rows when the question asks for distinct people or customers.

## Guided practice

1. Create a count plot for department.
2. Create a bar plot for mean satisfaction.
3. Add a point plot and compare its readability.
4. Create box and violin plots for ticket counts.
5. Overlay raw observations and explain what the summary chart hides.

## Independent practice

Choose a categorical variable and a numerical measure. Produce three charts that answer three different questions: count, estimated value and distribution. Write a short note explaining why the three charts are not interchangeable.

## Knowledge check

1. What does countplot count?
2. What does barplot estimate by default?
3. What does `errorbar` represent?
4. Why does a violin plot need enough observations?
5. When would you choose a strip plot over a bar plot?

## Lesson summary

Seaborn's categorical charts are not interchangeable. Count plots count records; bar and point plots estimate numerical summaries; box and violin plots show distributions; strip and swarm plots show observations. Understand the statistical meaning before choosing the function.