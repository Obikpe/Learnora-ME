# Lesson 12: Statistical Reasoning in Project Work

## Learning outcomes
Apply the professional method, produce a project artefact and communicate decisions with evidence.

## 1. Core explanation
Statistical reasoning helps distinguish patterns from random variation. A sample statistic describes the observed sample; inference uses assumptions to reason about a wider population. Confidence intervals express uncertainty around an estimate under a method's assumptions. A p-value is the probability of data at least as extreme under a specified null model; it is not the probability that the null hypothesis is true.

Effect size describes magnitude and is often more useful than statistical significance alone. A tiny difference can be statistically significant in a very large sample but unimportant in practice. Multiple comparisons increase the chance of finding apparently significant patterns by chance. Exploratory findings should be treated as hypotheses until confirmed.

Check sampling, independence, missingness, measurement and confounding. Statistical methods cannot repair a biased sample or poorly defined outcome. Report estimates with uncertainty and explain assumptions in plain language.

## 2. Worked example or template
Use the example in VS Code or adapt the structure to your project.

```python
import numpy as np
from scipy import stats

group_a = np.array([70, 72, 68, 75, 71, 69, 73, 74])
group_b = np.array([74, 76, 72, 78, 75, 77, 73, 79])
difference = group_b.mean() - group_a.mean()
test = stats.ttest_ind(group_b, group_a, equal_var=False)
print("Mean difference:", difference)
print("Welch t-test p-value:", test.pvalue)
```

## 3. Professional application
Keep the artefact reproducible and honest. State the data source, time period, methods, your contribution and limitations. Do not publish confidential data or make unsupported performance claims.

## 4. Guided practice
Interpret the mean difference and p-value. State what assumptions are needed and why the result does not by itself prove that a new teaching method caused an improvement.

## 5. Independent practice
Create or improve the corresponding project artefact. Ask another person to review it and record any unclear assumptions or missing instructions.

## 6. Knowledge check
1. What decision or audience does this artefact serve?
2. What evidence supports the claim?
3. Which limitations must be disclosed?
4. How can another person verify the work?

## Lesson summary
A professional portfolio demonstrates judgement, evidence, reproducibility and communication—not just familiarity with tools.