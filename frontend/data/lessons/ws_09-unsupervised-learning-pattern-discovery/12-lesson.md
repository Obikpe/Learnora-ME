# Lesson 12: Anomaly and Outlier Detection

## Learning outcomes

By the end of this lesson, you should be able to distinguish an outlier from an anomaly; explain isolation-based and neighbourhood-based approaches; use Isolation Forest and Local Outlier Factor; interpret anomaly scores and contamination settings; investigate flagged records; and explain why an anomaly is not proof of fraud or error.

![Anomaly detection flags unusual observations for review](/course-assets/ws09/anomaly-review.svg)

## 1. What is an anomaly?

An anomaly is an observation that differs substantially from an expected or common pattern under a chosen model or rule. Examples include an unusually high sensor temperature, an unexpected transaction amount or an unusually large change in a customer's behaviour.

An **outlier** is a value that lies far from other values in a statistical distribution. An **anomaly** is a broader contextual concept: the observation is unusual relative to a defined context, time, group or behaviour. A value can be an outlier but not a meaningful anomaly. A very high electricity reading may be normal during a known peak-demand period but unusual at midnight for that particular site.

The meaning of “unusual” must be defined. Is it unusual globally, within a machine, within a customer, within a time of day, or relative to recent history? Different definitions produce different results.

## 2. Why anomaly detection is often unsupervised

In many real situations, there are very few confirmed examples of the event we want to detect. A company may not have a reliable label for every fraudulent transaction or every failing sensor. Unsupervised and semi-supervised methods can identify unusual cases without requiring a complete set of labelled anomalies.

The result is a shortlist for investigation. A model cannot establish intent, cause or wrongdoing from unusualness alone. Human review and additional evidence are required.

## 3. Simple statistical approaches

For a roughly symmetric numeric distribution, a z-score describes how many standard deviations a value is from the mean:

```
z = (value - mean) / standard_deviation
```

A value with an absolute z-score above 3 is sometimes flagged for review. This is a rule of thumb, not a universal anomaly definition. It can perform poorly for skewed distributions, heavy tails, small samples and changing time patterns.

The interquartile range (IQR) is another robust summary. It is the difference between the 75th percentile (Q3) and 25th percentile (Q1). A common box-plot rule flags values below Q1 - 1.5×IQR or above Q3 + 1.5×IQR. These are potential outliers under the rule, not automatically errors.

Statistical thresholds are useful baselines because they are easy to explain. They may miss multivariate anomalies: a record can be ordinary on every individual feature but unusual when features are considered together.

## 4. Multivariate anomalies

Suppose a machine has normal temperature and normal vibration when considered separately. A particular observation has both values near their individual averages, but the combination is unusual because temperature and vibration normally rise together. A univariate threshold may miss this case.

Multivariate anomaly detection examines combinations of features. It depends on the representation, scaling, distribution and model assumptions. This is why preprocessing and contextual understanding remain essential.

## 5. Isolation Forest: unusual points are easier to isolate

Isolation Forest is based on the idea that unusual observations are often easier to separate from the rest of the data using random partitions.

Imagine repeatedly choosing a feature and a random split value. Common observations tend to require more splits before they become isolated. Unusual observations may be separated after fewer splits because they lie in sparse regions.

The method builds many random isolation trees. It combines the path lengths required to isolate observations and produces anomaly scores. The implementation exposes tools for predicting inliers and outliers.

## 6. Use Isolation Forest with scikit-learn

```python
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

readings = pd.DataFrame({
    "temperature": [20, 21, 20, 22, 21, 19, 20, 23, 21, 80],
    "vibration": [2.0, 2.1, 2.0, 2.2, 2.1, 1.9, 2.0, 2.3, 2.1, 9.5]
})

X = StandardScaler().fit_transform(readings)

model = IsolationForest(
    n_estimators=200,
    contamination=0.1,
    random_state=42
)
model.fit(X)

readings["prediction"] = model.predict(X)
readings["anomaly_score"] = model.decision_function(X)

print(readings)
```

Important settings and outputs:

- `n_estimators=200` builds 200 isolation trees. More trees can make scores more stable at additional computational cost.
- `contamination=0.1` tells the model to use an expected outlier proportion of 10% for setting the prediction threshold. It is not a statement that exactly 10% of the data is truly anomalous.
- `random_state=42` makes the random process reproducible.
- `predict` returns 1 for an inlier and -1 for an outlier under scikit-learn's convention.
- `decision_function` returns a score where lower values are more abnormal relative to the fitted model; the precise scale is model-specific.

The example is synthetic and contains one deliberately extreme record. Real data may be less obvious. Do not set contamination simply to the proportion you hope to find. Test how different thresholds affect review workload and missed cases.

## 7. Local Outlier Factor (LOF)

Local Outlier Factor compares the local density around an observation with the local densities around its neighbours. An observation may be unusual relative to its nearby neighbourhood even if it is not extreme globally.

For example, a temperature of 30 degrees may be common in one type of machine but unusual in another. LOF can identify local deviations when neighbourhoods are meaningful.

The main parameter `n_neighbors` controls how many nearby observations are considered. Too few neighbours can make the result noisy; too many can blur local patterns. LOF is sensitive to scaling and distance choice.

```python
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler

X = StandardScaler().fit_transform(readings[["temperature", "vibration"]])

lof = LocalOutlierFactor(n_neighbors=5, contamination=0.1)
labels = lof.fit_predict(X)

print(labels)  # 1 = inlier, -1 = outlier
```

By default, LOF is commonly used for novelty-free outlier detection on the data it is fitted to. If you need to score new future observations, consult the estimator's novelty mode and use the correct fit/predict workflow. Do not assume every outlier detector handles unseen data in the same way.

## 8. Investigate flags instead of accepting them blindly

For every flagged record, ask:
- Is the measurement valid, or could it be a data-entry or sensor error?
- Is there a known seasonal, operational or contextual explanation?
- Is the observation unusual globally or only within a particular group?
- Does the flag persist under reasonable preprocessing and parameter changes?
- What evidence is available outside the model?
- What harm could result from acting on a false positive?

Keep the original row, model version, score, threshold, date and investigation outcome. If analysts repeatedly review flags, those outcomes may eventually support a labelled evaluation dataset, subject to privacy and governance controls.

## 9. Evaluation without complete anomaly labels

Without known anomaly labels, ordinary precision and recall cannot be calculated reliably. You can still assess:
- Review yield: what proportion of flagged cases are judged worth investigating?
- Stability: do similar cases appear across reasonable model settings?
- Synthetic tests: does the method detect carefully designed unusual examples?
- Expert review: do domain specialists find the cases plausible?
- Operational burden: can the organisation investigate the number of alerts produced?

Synthetic tests do not prove performance on real anomalies. Expert review can also be biased. Document the evidence and limitations.

## 10. Common mistakes

- Calling every flagged observation fraud.
- Treating contamination as the true anomaly rate.
- Ignoring local context and seasonality.
- Failing to scale features for distance-based detectors.
- Removing outliers automatically before understanding them.
- Using a model score as a probability when it is not calibrated as one.
- Reporting only the number of flags without reviewing examples.

## 11. Guided practice

Create a dataset of ordinary daily temperature readings and one unusually high reading. Calculate z-scores and IQR fences. Explain why the flagged reading should be investigated rather than deleted automatically. Then describe how a combination of temperature and vibration could reveal a multivariate anomaly.

## 12. Independent practice

Choose a public or synthetic numeric dataset. Fit Isolation Forest and LOF after justified preprocessing. Compare the observations flagged by each method, inspect their original values and explain differences. Write an investigation protocol that states what evidence would confirm, explain or dismiss a flag.

## 13. Knowledge check

1. How is an anomaly different from a simple outlier?
2. Why can univariate thresholds miss multivariate anomalies?
3. What is the central idea behind Isolation Forest?
4. What does LOF compare?
5. In scikit-learn's common prediction convention, what does -1 represent?
6. Why is contamination not necessarily the true anomaly proportion?
7. Why must a flagged record be investigated before action is taken?

## Lesson summary

Anomaly detection identifies observations that are unusual under a chosen representation and model. Statistical rules provide transparent baselines; Isolation Forest isolates unusual points through random partitions; LOF compares local density. A flag is a prompt for review, never proof of fraud, fault or intent. Context, validation, documentation and human investigation are essential.
