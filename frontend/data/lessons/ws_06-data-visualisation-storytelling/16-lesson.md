# Lesson 16: Uncertainty, Error Bars and Statistical Estimation

## Learning outcomes
You should be able to distinguish mean, median, standard deviation, standard error and confidence interval; add error bars to Matplotlib and Seaborn charts; explain bootstrap intuition; choose uncertainty displays; and avoid interpreting intervals incorrectly.

## 1. Why show uncertainty?
A chart often displays an estimate such as an average score or conversion rate. Estimates vary because we observe a sample rather than the entire population. Measurements may also be imprecise or incomplete.

Distinguish:
- Observed values: individual records.
- Descriptive spread: variation among those records.
- Uncertainty in an estimate: how much the estimate may vary across repeated samples under a statistical model.

These are not interchangeable.

## 2. Mean, median and standard deviation
The mean is the sum divided by the number of values and is sensitive to extreme values. The median is the middle value after sorting and is more resistant to extremes. Standard deviation describes spread around the mean; it does not directly measure uncertainty about the mean.

```python
import numpy as np
scores = np.array([55, 60, 62, 65, 67, 68, 70, 72, 75, 95])
print("Mean:", scores.mean())
print("Median:", np.median(scores))
print("Sample standard deviation:", scores.std(ddof=1))
```

`ddof=1` uses the sample correction. A population standard deviation uses a different convention.

## 3. Standard error
For independent observations, the standard error of the sample mean is commonly estimated as:

`SE = s / sqrt(n)`

where s is the sample standard deviation and n is sample size. Standard error describes estimated sampling variability of the mean. It is not the spread of individual observations.

## 4. Matplotlib error bars
```python
import matplotlib.pyplot as plt
groups = ["A", "B", "C"]
means = [68, 74, 71]
standard_errors = [2.5, 3.0, 1.8]

fig, ax = plt.subplots(figsize=(7, 4))
ax.errorbar(groups, means, yerr=standard_errors,
            fmt="o", markersize=8, capsize=5)
ax.set(title="Group means with ±1 standard error",
       xlabel="Group", ylabel="Mean score")
plt.show()
```

- `yerr` supplies vertical error sizes.
- `fmt="o"` draws circular markers.
- `capsize` controls end caps.
- `markersize` controls point size.

The title explicitly says ±1 standard error. Without a label, the reader cannot know what the bars represent.

## 5. Confidence intervals
A confidence interval is produced by a procedure with a stated long-run coverage rate. A 95% confidence procedure is designed so that 95% of intervals constructed from repeated samples would contain the fixed population parameter, under the method's assumptions.

It is not precise to say that a frequentist 95% confidence interval gives a 95% probability that the already-fixed parameter lies inside this particular interval. The 95% refers to long-run coverage of the procedure.

## 6. Bootstrap intuition
Bootstrapping repeatedly samples observations with replacement from the observed dataset, calculates a statistic for each resample, and uses the resulting distribution to estimate uncertainty.

```python
import numpy as np
rng = np.random.default_rng(42)
values = np.array([55, 60, 62, 65, 67, 68, 70, 72, 75, 95])

bootstrap_means = []
for _ in range(5000):
    sample = rng.choice(values, size=len(values), replace=True)
    bootstrap_means.append(sample.mean())

lower, upper = np.percentile(bootstrap_means, [2.5, 97.5])
print("Observed mean:", values.mean())
print("Bootstrap percentile interval:", lower, upper)
```

This is a simple percentile bootstrap. It assumes the sample represents the population and observations can be resampled independently. Clustered, time-dependent or complex survey data require different resampling strategies.

## 7. Seaborn estimation plots
```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.DataFrame({
    "group": ["A"] * 6 + ["B"] * 6,
    "score": [60, 62, 65, 67, 68, 70, 65, 70, 72, 75, 78, 80]
})
fig, ax = plt.subplots(figsize=(7, 4))
sns.pointplot(data=df, x="group", y="score",
              estimator="mean", errorbar=("ci", 95),
              n_boot=2000, ax=ax)
ax.set(title="Mean score with 95% confidence intervals",
       ylabel="Mean score")
plt.show()
```

`estimator` specifies the summary; `errorbar=("ci", 95)` requests a 95% confidence interval; `n_boot` controls bootstrap resamples. The exact procedure depends on Seaborn version and settings. Describe the method used.

## 8. Compare uncertainty measures

| Quantity | Meaning |
|---|---|
| Standard deviation | Spread of individual observations |
| Standard error | Estimated sampling variability of an estimator |
| Confidence interval | Interval from a procedure with stated long-run coverage |

Do not swap these labels because all can be drawn as error bars.

## 9. Uncertainty in proportions
A percentage without a denominator can mislead. A 50% conversion rate from 2 visitors is less informative than 50% from 20,000 visitors. Show sample size and use a proportion interval method appropriate to the design. Clustered or repeated observations may invalidate simple independent-observation intervals.

## 10. Common mistakes
- Calling standard deviation standard error.
- Labelling every error bar a confidence interval.
- Treating overlapping intervals as a universal significance test.
- Omitting sample sizes.
- Ignoring clustering or time dependence.
- Presenting a narrow interval from a biased sample as certainty.

## Guided practice
1. Calculate mean, median and standard deviation.
2. Calculate standard error.
3. Plot mean ±1 standard error.
4. Run the bootstrap example with different numbers of resamples.
5. Explain what the bootstrap assumes.

## Independent practice
Choose a group comparison with sufficient observations. Display an estimate and a clearly defined interval. Include sample sizes, method, assumptions and limitations. State whether the bars describe individual spread or uncertainty in an estimate.

## Knowledge check
1. What does standard deviation measure?
2. How is standard error different?
3. What does a 95% confidence procedure mean?
4. Why bootstrap with replacement?
5. Why should sample sizes be shown?

## Lesson summary
Uncertainty is part of the evidence. Distinguish spread from uncertainty in an estimate, label error bars precisely, show denominators and use methods appropriate to the sampling design.