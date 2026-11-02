# Lesson 13: Statistical Uncertainty and Honest Charts

## Learning outcomes
Explain the visualisation method, implement the worked example in Python, interpret it and communicate its limitations.

## 1. Core explanation
Every chart contains uncertainty from sampling, measurement, missingness and modelling choices. A point estimate is not the whole story. Error bars may represent standard deviation, standard error or a confidence interval; these are different quantities and must be labelled. Overlapping intervals do not automatically prove that two groups are equal, and non-overlap is not a universal significance test.

Show sample sizes and denominators. For proportions, uncertainty depends on the number of observations. For time series, observations may be autocorrelated, so a simple independent-sample interval may be inappropriate. Avoid plotting a smooth trend line without explaining the method.

Honest charts use suitable scales, include relevant context and avoid false precision. If an axis is truncated, disclose it. Do not remove inconvenient observations without a documented reason. State whether intervals represent variability in the data or uncertainty about an estimated quantity.

## 2. Worked Python example
Run in VS Code. Install required packages with `python -m pip install pandas numpy matplotlib seaborn plotly`.

```python
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(5)
groups = [rng.normal(70, 8, 35), rng.normal(74, 9, 40), rng.normal(72, 7, 12)]
means = [g.mean() for g in groups]
sems = [g.std(ddof=1) / np.sqrt(len(g)) for g in groups]
plt.errorbar(["A", "B", "C"], means, yerr=sems, fmt="o", capsize=5)
plt.ylabel("Mean score"); plt.title("Group means with standard-error bars")
plt.show()
print("Sample sizes:", [len(g) for g in groups])
```

## 3. Interpretation and design checks
State the analytical question, population, variables, units and denominator. Check missingness and sample size. Distinguish observations from explanations and recommendations. Design for the actual audience and the size at which the visual will be viewed.

## 4. Guided practice
Change the sample size of group C and observe how standard error changes. Write a chart caption that explains what the error bars represent and why they should not be called a 95% confidence interval.

## 5. Independent practice
Apply the lesson to a dataset. Create a chart or artefact, write a caption that states the main message and caveat, and ask another person to interpret it without your explanation.

## 6. Knowledge check
1. What question does this visual answer?
2. Which encoding or design choice supports the comparison?
3. What could mislead the audience?
4. What uncertainty or limitation must be disclosed?

## Lesson summary
Effective visual communication combines accurate encoding, clear context, audience-aware design and honest interpretation.