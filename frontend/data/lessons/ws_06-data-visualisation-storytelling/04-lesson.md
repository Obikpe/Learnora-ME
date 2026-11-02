# Lesson 4: Histograms, Frequency and Density

## Learning outcomes
You should be able to distinguish a histogram from a bar chart; explain bins, frequency, relative frequency and density; build histograms with `ax.hist()`; choose bin widths; overlay density curves; create cumulative views; and explain when a histogram is and is not suitable.

## 1. Why use a histogram?

A histogram shows the distribution of a numerical variable. A distribution describes the values that occur and how often they occur. It can reveal the centre, spread, skewness, multiple peaks, gaps and unusual observations.

Imagine scores from 500 learners. A table of all 500 scores is difficult to scan. A histogram groups values into intervals called **bins**. The height of each bar tells how many observations fall within that interval (or a related frequency/density measure).

A histogram answers questions such as:
- Are most scores low, middle or high?
- Is the distribution symmetric or skewed?
- Are there two peaks, suggesting different subgroups?
- Are there unusually extreme values?
- Is the spread narrow or wide?

Use a histogram for a numerical variable. Do not use it for names such as department or region. Use a bar chart for categories.

## 2. Bins and bin edges

A **bin** is an interval of numerical values. Suppose scores range from 0 to 100. You might choose intervals 0–10, 10–20, 20–30 and so on. The boundaries separating intervals are called **bin edges**.

The number and width of bins change the picture:

- Too few wide bins can hide important structure.
- Too many narrow bins can make random noise look like meaningful patterns.
- Different bin widths can make two histograms difficult to compare.

There is no single perfect bin count for every dataset. Try a sensible starting rule, inspect the result and explain your choice. For formal comparisons, use consistent bin edges across groups.

## 3. The Matplotlib function: ax.hist()

The general form is:

```python
ax.hist(values, bins=10, range=None, density=False,
        cumulative=False, histtype="bar", alpha=1.0,
        edgecolor=None, label=None)
```

Important arguments:

- `values`: numerical observations.
- `bins`: number of bins, a sequence of bin edges, or a rule such as `"auto"`.
- `range`: lower and upper range to include.
- `density=False`: plot counts by default; if True, normalise so the total histogram area is 1.
- `cumulative=True`: show cumulative counts or cumulative density.
- `histtype`: commonly `"bar"`, `"step"` or `"stepfilled"`.
- `alpha`: transparency.
- `edgecolor`: border colour.
- `label`: legend label.

## 4. First histogram

```python
import matplotlib.pyplot as plt

scores = [45, 52, 58, 60, 61, 63, 64, 65, 66, 67,
          68, 69, 70, 71, 72, 73, 74, 75, 77, 80,
          82, 85, 88, 91, 95]

fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(scores, bins=8, color="cornflowerblue",
        edgecolor="white")
ax.set(title="Distribution of learner scores",
       xlabel="Score (out of 100)", ylabel="Number of learners")
plt.show()
```

The y-axis says “Number of learners” because `density` is left at its default value, False. Each bar's height is the number of scores inside that bin.

## 5. Choose bin edges deliberately

You can let Matplotlib choose a binning rule:

```python
ax.hist(scores, bins="auto")
```

Or specify a number:

```python
ax.hist(scores, bins=10)
```

Or supply exact edges:

```python
edges = [0, 20, 40, 60, 80, 100]
ax.hist(scores, bins=edges)
```

Explicit edges are useful when comparing the same measurement across cohorts or years. If one group uses 0–10, 10–20 and another uses 0–5, 5–10, their bar heights cannot be compared directly.

## 6. Frequency versus density

**Frequency** is a count. **Relative frequency** is a proportion of all observations. **Probability density** is scaled so that the total area under the histogram equals 1.

When bins have equal width, count heights are easy to compare. When bins have unequal widths, raw counts alone can be misleading because wider intervals have more opportunity to contain observations. Density accounts for bin width.

```python
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(scores, bins=8, density=True,
        color="darkorange", edgecolor="white")
ax.set(title="Score distribution (probability density)",
       xlabel="Score", ylabel="Density")
plt.show()
```

The y-axis is not the number of learners. The height is density; the area of a bar represents the proportion of observations in that interval.

## 7. Compare two distributions

Overlaying distributions helps compare groups. Use transparency or outline histograms so one group does not completely hide the other:

```python
import matplotlib.pyplot as plt

class_a = [55, 61, 63, 65, 67, 69, 70, 72, 74, 77, 81, 85]
class_b = [48, 52, 58, 60, 62, 64, 66, 68, 70, 72, 74, 78]

bins = range(40, 101, 10)
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(class_a, bins=bins, alpha=0.55, label="Class A")
ax.hist(class_b, bins=bins, alpha=0.55, label="Class B")
ax.set(title="Score distributions by class",
       xlabel="Score", ylabel="Learners")
ax.legend()
plt.show()
```

The same bin edges are used for both groups. This is important. If the distributions overlap heavily, use side-by-side histograms, density curves or a box/violin plot rather than trying to decode two layers of bars.

## 8. Cumulative histograms

A cumulative histogram answers “how many observations are at or below this value?”:

```python
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(scores, bins=10, cumulative=True,
        histtype="step", linewidth=2)
ax.set(title="Cumulative number of scores",
       xlabel="Score", ylabel="Cumulative learners")
plt.show()
```

With `cumulative=True`, each step includes the observations in the current and all earlier bins. This is useful for threshold questions such as “How many learners scored 70 or below?” The exact answer depends on the bin edges, so do not treat the step as an exact empirical cumulative distribution unless the bins are sufficiently fine or you use a dedicated ECDF.

## 9. Histogram and KDE: different views

A **kernel density estimate (KDE)** is a smoothed estimate of a distribution. It replaces bars with a smooth curve. Smoothing depends on a bandwidth parameter: too much smoothing hides features; too little creates a noisy curve. A KDE can extend beyond the actual minimum and maximum, so it should not be mistaken for observed values.

Seaborn will be taught in detail later. For now, see the idea:

```python
import seaborn as sns
import matplotlib.pyplot as plt

sns.histplot(x=scores, bins=8, stat="density",
             kde=True, edgecolor="white")
plt.xlabel("Score")
plt.ylabel("Density")
plt.title("Score distribution with a smoothed density estimate")
plt.show()
```

The histogram shows binned observations; the KDE is a model-based smooth summary. They answer related but not identical questions.

## 10. When not to use a histogram

- For categories: use a bar or count chart.
- For a tiny sample: show individual points or a dot plot as well.
- For multiple groups with different bin edges: standardise the bins first.
- For strongly skewed values: consider a log scale only when values are positive and the transformation is explained.
- For exact threshold counts: calculate the count directly rather than estimating it visually.

## 11. Guided practice

1. Plot the score list with 5, 10 and 20 bins.
2. Explain what detail appears or disappears.
3. Change `density=False` to `density=True` and rewrite the y-axis label.
4. Compare two classes using identical bin edges.
5. Create a cumulative histogram and answer a threshold question.

## 12. Independent practice

Choose a numerical variable with at least 100 observations. Make a histogram using an explicitly justified bin choice. Make a second version with a different bin count and explain why the apparent shape changes. Report the sample size, units, centre, spread, skewness or multiple peaks if visible, and any limitation.

## Knowledge check

1. What is a bin?
2. How is a histogram different from a bar chart?
3. What does `density=True` change?
4. Why should two group histograms use the same bin edges?
5. What does a KDE curve represent, and why can smoothing mislead?

## Lesson summary

Histograms show how numerical observations are distributed. The choice of bins is part of the analysis, not a cosmetic setting. Always label whether the y-axis represents counts or density, use consistent bins for comparisons and consider individual observations or other distribution charts when the sample is small.