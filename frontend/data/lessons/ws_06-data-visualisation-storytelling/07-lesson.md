# Lesson 7: Box Plots, Violin Plots and Category Distributions

## Learning outcomes
You should be able to explain median, quartiles, interquartile range and whiskers; create Matplotlib box plots; compare distributions across groups; understand violin plots and density; add individual observations with strip or swarm plots; and explain the limits of outlier rules.

## 1. Why compare distributions by group?

Averages alone can hide important differences. Two classes can have the same mean score while one class has scores tightly clustered around the mean and another has very high and very low scores.

Distribution charts show spread and shape. They help answer:
- Which group has the higher typical value?
- Which group has more variation?
- Are there unusual observations?
- Are the distributions symmetric or skewed?
- Do groups overlap?

A box plot gives a compact summary. A violin plot shows a smoothed distribution shape. A strip or swarm plot shows individual observations.

## 2. Understand a box plot

A standard box plot contains:

- **Median:** the middle value when observations are sorted.
- **First quartile (Q1):** the 25th percentile; about one quarter of observations are at or below it.
- **Third quartile (Q3):** the 75th percentile.
- **Interquartile range (IQR):** Q3 minus Q1; the width of the middle half of the data.
- **Box:** extends from Q1 to Q3.
- **Median line:** drawn inside the box.
- **Whiskers:** extend to the most extreme data points within the usual 1.5 × IQR rule.
- **Flier points:** observations beyond the whiskers under that rule.

The whiskers do not necessarily show the minimum and maximum. The default Matplotlib box plot uses the 1.5 × IQR convention. A point beyond a whisker is not automatically an error or an invalid value. It is an observation worth investigating.

## 3. Create a Matplotlib box plot

```python
import matplotlib.pyplot as plt

class_a = [52, 58, 60, 62, 64, 65, 66, 68, 70, 72, 75]
class_b = [40, 50, 57, 61, 65, 67, 70, 73, 78, 85, 96]
class_c = [60, 62, 63, 64, 65, 65, 66, 67, 68, 69, 70]

fig, ax = plt.subplots(figsize=(8, 5))
ax.boxplot([class_a, class_b, class_c],
           tick_labels=["Class A", "Class B", "Class C"],
           showmeans=True, patch_artist=True)
ax.set(title="Score distributions by class",
       xlabel="Class", ylabel="Score")
plt.show()
```

- The list passed to `boxplot()` contains one sequence per group.
- `tick_labels` names the groups.
- `showmeans=True` adds a mean marker.
- `patch_artist=True` allows the box areas to be filled with colour.

The mean and median are different summaries. If the distribution is skewed, they can be far apart. The median is often more robust to extreme values.

## 4. Customise a box plot

```python
fig, ax = plt.subplots(figsize=(8, 5))
result = ax.boxplot(
    [class_a, class_b, class_c],
    tick_labels=["A", "B", "C"],
    patch_artist=True,
    showmeans=True,
    notch=False,
    widths=0.55,
    medianprops={"color": "darkred", "linewidth": 2},
    meanprops={"marker": "D", "markerfacecolor": "gold"},
    flierprops={"marker": "o", "markerfacecolor": "orange",
                "markersize": 5, "alpha": 0.7}
)
ax.set_ylabel("Score")
ax.set_title("Customised score box plots")
plt.show()
```

The returned dictionary contains plotted components such as boxes, medians, whiskers, caps, means and fliers. This allows more detailed formatting. Keep the design consistent across groups so the comparison remains fair.

## 5. Understand a violin plot

A violin plot combines a distribution summary with a smoothed density shape. The width at a given y-value indicates how concentrated observations are around that value. A wider section means more observations are estimated near that level.

The shape is produced by kernel density estimation (KDE). It is a smoothed estimate, not a literal outline of the data. The appearance depends on bandwidth and sample size. A violin plot can suggest multiple peaks, but small samples can produce unstable shapes.

Seaborn makes violin plots straightforward:

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.DataFrame({
    "class": ["A"] * len(class_a) + ["B"] * len(class_b) + ["C"] * len(class_c),
    "score": class_a + class_b + class_c
})

fig, ax = plt.subplots(figsize=(8, 5))
sns.violinplot(data=df, x="class", y="score",
               inner="quart", cut=0, ax=ax)
ax.set_title("Score distributions by class")
plt.show()
```

- `data=df` provides the table.
- `x="class"` selects the grouping column.
- `y="score"` selects the numerical variable.
- `inner="quart"` displays quartile information inside the violin.
- `cut=0` prevents the KDE from extending beyond the observed data range.
- `ax=ax` tells Seaborn to draw on the Matplotlib Axes we created.

## 6. Show individual observations: strip and swarm plots

A box plot summarises data and can hide the number of observations. A strip plot overlays individual points with small horizontal jitter:

```python
fig, ax = plt.subplots(figsize=(8, 5))
sns.stripplot(data=df, x="class", y="score",
              jitter=0.15, alpha=0.7, ax=ax)
ax.set_title("Individual scores by class")
plt.show()
```

A swarm plot adjusts point positions to reduce overlap:

```python
fig, ax = plt.subplots(figsize=(8, 5))
sns.swarmplot(data=df, x="class", y="score",
              size=5, ax=ax)
ax.set_title("Non-overlapping individual scores by class")
plt.show()
```

Swarm plots become slow or crowded with large datasets. For thousands of observations, a violin, box or distribution chart may be more practical.

## 7. Combine a summary and the raw points

A box plot with a strip plot can show both summary and individual records:

```python
fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(data=df, x="class", y="score",
            showfliers=False, color="lightgray", ax=ax)
sns.stripplot(data=df, x="class", y="score",
              color="navy", alpha=0.65, jitter=0.12, ax=ax)
ax.set_title("Class score summaries and individual learners")
plt.show()
```

Here, `showfliers=False` hides the separate box-plot outlier markers because the strip plot already shows all individual observations. It does not remove those observations from the data.

## 8. Which distribution chart should you choose?

- **Box plot:** compact comparison of medians, quartiles and potential outliers.
- **Violin plot:** compare distribution shape and concentration; use caution with small samples.
- **Strip plot:** show individual observations when the dataset is not too large.
- **Swarm plot:** show individual points while reducing overlap; not ideal for huge datasets.
- **Histogram:** inspect the distribution of one numerical variable, especially when bins and frequency matter.

For small samples, raw points are often more informative than a violin's smoothed density. For a report with many groups, box plots may be more compact.

## 9. Common mistakes

- Calling every point beyond a whisker a data error.
- Assuming whiskers always show minimum and maximum.
- Comparing violin shapes without considering sample sizes.
- Using a swarm plot with thousands of points.
- Showing only the mean when spread and skewness matter.
- Hiding group sample sizes when groups are very unequal.

## Guided practice

1. Create box plots for three classes.
2. Identify the median and IQR for each group.
3. Add mean markers and compare mean versus median.
4. Create violin plots and explain what the width means.
5. Overlay individual points and identify what the summary hid.

## Independent practice

Choose a numerical variable and a categorical grouping variable. Produce a box plot and a violin or strip plot. Report group sizes, medians and spread. Investigate unusual observations rather than deleting them automatically. Justify which visual is most appropriate for the sample size.

## Knowledge check

1. What is the IQR?
2. How are box-plot whiskers commonly determined?
3. Does an outlier marker prove that a value is invalid?
4. What does the width of a violin plot represent?
5. Why might a strip plot be preferable for a small dataset?

## Lesson summary

Distribution comparisons require more than group averages. Box plots summarise quartiles and potential outliers; violin plots show smoothed density; strip and swarm plots reveal individual observations. Choose according to sample size and analytical purpose, and investigate unusual points rather than automatically removing them.