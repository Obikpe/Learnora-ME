# Lesson 10: Seaborn Distribution Visualisation

## Learning outcomes
You should be able to use Seaborn's `histplot()`, `kdeplot()`, `ecdfplot()` and `displot()`; choose bins and normalisation; compare distributions using hue; explain KDE bandwidth and cumulative distributions; and select a distribution view appropriate to sample size and analytical question.

## 1. What does distribution analysis tell us?

A distribution describes how values are spread. It includes the centre, spread, shape, skewness, peaks, gaps and tails. Distribution charts help an analyst understand data before calculating averages or fitting models.

For example, the mean salary can be strongly affected by a few very high salaries. A histogram, box plot or ECDF may show that the majority of salaries are much lower than the mean. Always inspect the distribution before deciding which summary statistics are useful.

## 2. Prepare example data

```python
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

rng = np.random.default_rng(12)
df = pd.DataFrame({
    "score": np.concatenate([
        rng.normal(65, 8, 120),
        rng.normal(78, 5, 80)
    ]),
    "cohort": ["A"] * 120 + ["B"] * 80
})
df["score"] = df["score"].clip(0, 100)
sns.set_theme(style="whitegrid")
```

The example creates two groups with different centres and spreads. Random data changes if the seed changes. The seed is fixed here so the example is reproducible.

## 3. histplot(): histogram and optional KDE

`histplot()` is an axes-level function for histograms:

```python
fig, ax = plt.subplots(figsize=(8, 4))
sns.histplot(data=df, x="score", bins=15, ax=ax)
ax.set_title("Learner score distribution")
ax.set_xlabel("Score")
ax.set_ylabel("Number of learners")
plt.show()
```

Important arguments:
- `data`: DataFrame containing the variable.
- `x` or `y`: variable to distribute.
- `bins`: number of bins, binning rule or explicit bin edges.
- `binwidth`: width of each bin.
- `binrange`: lower and upper limits for binning.
- `stat`: `"count"`, `"frequency"`, `"probability"`, `"percent"` or `"density"`.
- `hue`: group variable.
- `multiple`: how hue groups are displayed; common options include `"layer"`, `"stack"`, `"dodge"` and `"fill"`.
- `kde=True`: add a smoothed density estimate.
- `element`: visual form such as `"bars"`, `"step"` or `"poly"`.

The default y-axis is count. If you use `stat="percent"`, the axis is percentage rather than number of records. Change the label to match.

## 4. Compare groups using hue

```python
fig, ax = plt.subplots(figsize=(8, 4))
sns.histplot(data=df, x="score", hue="cohort",
             bins=15, element="step", stat="density",
             common_norm=False, ax=ax)
ax.set_title("Score distributions by cohort")
ax.set_ylabel("Density")
plt.show()
```

- `hue="cohort"` draws separate group distributions.
- `element="step"` uses outlines instead of filled bars.
- `stat="density"` expresses density rather than raw count.
- `common_norm=False` normalises each group independently so each group's density integrates to one.

This makes shapes easier to compare, but it hides differences in group size. If group size matters, show sample sizes or use a count-based chart too.

The `multiple` argument changes how group histograms combine:
- `"layer"`: draw distributions over one another.
- `"stack"`: stack counts or densities.
- `"dodge"`: place bars beside one another.
- `"fill"`: scale each bin to show proportions across groups.

Choose the option that matches the question, and check the denominator represented by the y-axis.

## 5. kdeplot(): smoothed density

A KDE (kernel density estimate) estimates a smooth distribution from observations. Each data point contributes a small smooth curve; the curves are combined into an overall estimate.

```python
fig, ax = plt.subplots(figsize=(8, 4))
sns.kdeplot(data=df, x="score", hue="cohort",
            fill=True, alpha=0.25, common_norm=False,
            bw_adjust=1, ax=ax)
ax.set_title("Smoothed score distributions")
ax.set_ylabel("Density")
plt.show()
```

Important arguments:
- `fill`: fill the area under the curve.
- `bw_adjust`: multiply the default bandwidth. Larger values smooth more; smaller values preserve more local variation but can become noisy.
- `cut`: how far the curve may extend beyond observed extremes; `cut=0` stops at the data boundaries.
- `clip`: restrict the estimate to a specified range.
- `common_norm`: whether group densities share a common normalisation.

KDE is not a histogram and does not show actual counts per bin. It is an estimated smooth density. With small samples or discrete variables, a KDE may suggest a shape that the data does not support.

## 6. ecdfplot(): empirical cumulative distribution

An empirical cumulative distribution function (ECDF) answers: what proportion of observations are less than or equal to a given value?

```python
fig, ax = plt.subplots(figsize=(8, 4))
sns.ecdfplot(data=df, x="score", hue="cohort", ax=ax)
ax.set(title="Cumulative proportion of scores",
       xlabel="Score", ylabel="Proportion at or below score")
plt.show()
```

The curve rises from 0 toward 1. If the curve for one group is consistently further to the right, that group tends to have higher values. ECDFs avoid bin-width choices and KDE smoothing. They are especially useful for comparing percentiles and thresholds.

## 7. displot(): figure-level distribution chart

`displot()` is figure-level. It creates its own Figure and can create facets:

```python
grid = sns.displot(data=df, x="score", col="cohort",
                   kind="hist", bins=12, height=4, aspect=1.1)
grid.set_axis_labels("Score", "Learners")
grid.set_titles("Cohort {col_name}")
plt.show()
```

- `col="cohort"` creates one panel per cohort.
- `kind="hist"` selects a histogram.
- `height` controls panel height in inches.
- `aspect` controls width relative to height.

You do not pass `ax=` because `displot()` manages the Figure and its axes. Its return value is a FacetGrid-like object; use grid methods such as `set_axis_labels()` to customise the panels.

## 8. Which distribution chart should you choose?

- Histogram: counts and shape, with a bin-width decision.
- KDE: smooth density shape, with bandwidth sensitivity.
- ECDF: exact cumulative proportion without bins.
- Box plot: compact median, quartiles and outlier summary.
- Violin plot: group density shape, with smoothing caveats.

For a small sample, show individual points. For a skewed distribution, include a median and percentiles rather than relying only on the mean.

## 9. Common mistakes

- Calling a KDE curve the actual observed distribution.
- Using too much smoothing and hiding multiple peaks.
- Comparing group densities without explaining whether they are normalised separately.
- Forgetting that `stat="percent"` changes the y-axis meaning.
- Using a histogram with different bin widths for group comparisons.
- Using a KDE for a tiny sample or a discrete variable without caution.

## Guided practice

1. Make a histogram with 8, 15 and 30 bins.
2. Overlay cohort distributions with `hue`.
3. Change `multiple` from `layer` to `stack` and `fill`.
4. Add a KDE and change `bw_adjust`.
5. Plot an ECDF and estimate the proportion scoring 70 or below.

## Independent practice

Use a dataset with a numerical measure and a meaningful group. Produce a histogram, KDE and ECDF. State what each reveals, which choices affect the appearance and which visual is most suitable for comparing thresholds. Include group sizes.

## Knowledge check

1. What is a bin?
2. What does `stat="density"` mean?
3. What does KDE bandwidth control?
4. How does an ECDF differ from a histogram?
5. What is the difference between `histplot()` and `displot()`?

## Lesson summary

Seaborn's distribution functions answer related but different questions. `histplot()` shows binned counts or density; `kdeplot()` estimates a smooth density; `ecdfplot()` shows cumulative proportions; and `displot()` manages figure-level distribution views and facets. Choose the representation according to the question, sample size and assumptions.