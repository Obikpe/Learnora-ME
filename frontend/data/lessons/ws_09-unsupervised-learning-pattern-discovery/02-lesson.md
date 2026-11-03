# Lesson 2: Preparing Data Without a Target

## Learning outcomes

By the end of this lesson, you should be able to Prepare a feature matrix without a target; inspect missingness, types and scales; choose defensible transformations; and explain how feature representation affects distance-based methods.

![Unsupervised analysis workflow: features become patterns that must be validated](/course-assets/ws09/clustering-concepts.svg)

## 1. Core explanation
Without a target, feature selection depends on the question and the concept you want the algorithm to represent. For customer segmentation, transaction frequency, average basket size and recency may be meaningful. Customer ID is not a behavioural measure. For document clustering, word or embedding features represent text content. Irrelevant features can dominate distances and obscure useful structure.

Inspect missingness, duplicates, extreme values and feature distributions. Impute or remove missing records only with a defensible reason. Convert categories thoughtfully. Standardise numeric fields when distance-based algorithms are used; otherwise a large-unit feature can dominate. For skewed positive variables, a log transform may reduce extreme scale differences.

Do not include target-like outcomes or variables created after the observation time. Even without labels, leakage can make clusters reflect information unavailable for the intended use. Preserve a record of transformations so cluster profiles can be interpreted in the original units.

## 2. Worked Python example
Run in VS Code. Install relevant packages with `python -m pip install numpy pandas matplotlib scipy scikit-learn`. Some scikit-learn dataset loaders may require internet access on first use.

```python
import pandas as pd
from sklearn.preprocessing import StandardScaler

customers = pd.DataFrame({
    "recency_days": [5, 12, 60, 90, 8],
    "orders_90d": [12, 8, 1, 0, 10],
    "avg_basket": [35, 42, 18, 12, 39]
})
scaled = StandardScaler().fit_transform(customers)
print(pd.DataFrame(scaled, columns=customers.columns).round(2))
```

## 3. Interpretation
Describe the feature representation, distance or objective, model settings and what the output means. Cluster IDs are arbitrary. An anomaly flag is a prompt for investigation, not proof of misconduct. Validate any discovered pattern in original units and with domain knowledge.

## 4. Guided practice
Add a customer identifier column and observe what happens if you include it in clustering. Explain why arbitrary IDs should normally be excluded and why scaling is needed for these variables.

## 5. Independent practice
Choose a dataset and state the purpose of the unsupervised analysis. Compare at least two parameter settings. Profile the resulting groups or flagged cases and document stability, limitations and possible actions.

## 6. Knowledge check
1. What structure is the algorithm attempting to discover?
2. Which assumptions are introduced by the distance or representation?
3. How can you tell whether the result is useful rather than merely computable?
4. What should not be inferred from the output?

## Lesson summary
Unsupervised algorithms find patterns according to mathematical definitions. Human interpretation, stability checks and practical validation determine whether those patterns deserve to be used.

## Deeper explanation: feature design defines similarity

Preprocessing is not merely cleaning a spreadsheet. It determines what the algorithm is allowed to regard as similar. Two customers with equal order frequency but different basket sizes may be grouped if spend is omitted and separated if spend is included. Neither outcome is inherently correct; the right representation depends on the question.

Audit every feature for meaning and units, availability at the intended decision time, scale, redundancy, missingness and sensitivity. Exclude identifiers because arbitrary numbers do not represent behaviour. Exclude post-outcome variables because they introduce information unavailable at the intended time. A feature can be mathematically valid yet conceptually irrelevant.

A common numeric pipeline is median imputation followed by standardisation. Median imputation replaces missing values with the feature median. Standardisation subtracts the feature mean and divides by its standard deviation. This places numeric columns on comparable scales, but does not make them equally meaningful or fair. A noisy feature can still distort distance after scaling.

For reproducibility, fit transformations as part of a pipeline and reuse the fitted pipeline for future data. Do not independently scale a future dataset using different means and standard deviations. For mixed numeric and categorical data, consider a representation and distance designed for mixed types; one-hot encoding can create many dimensions and alter the meaning of distance.

**Practice:** Build two defensible feature sets for the same analytical question. Compare their results and explain which assumptions changed. If the conclusions change dramatically, report the sensitivity instead of hiding it.

### Worked example: why scaling changes the answer

Consider two measurements: annual spend in naira, ranging from 5,000 to 500,000, and order count, ranging from 1 to 20. Under raw Euclidean distance, a spend difference of 100,000 can dominate a difference of several orders. The algorithm may effectively group customers by spend alone, even if frequency is equally important to the business question.

Standardisation converts each feature into a number of standard deviations from its mean. This reduces the influence of units, but it does not decide the correct business weights. If frequency should matter twice as much as spend, that weighting needs a documented reason and a sensitivity check.

Fit the scaler on the dataset used to establish the representation and preserve it for later scoring. If the mean or standard deviation changes unexpectedly, the coordinates change too. Keep an unscaled copy for profiling and explaining the segments in familiar units.
