# Lesson 12: Anomaly and Outlier Detection

## Learning outcomes

By the end of this lesson, you should be able to Fit Isolation Forest to identify unusual observations; explain contamination and anomaly scores; distinguish anomalies from errors or fraud; and design a human investigation process.

![Anomaly detection flags cases for human review](/course-assets/ws09/anomaly-review.svg)

## 1. Core explanation
Anomaly detection identifies observations that differ from the majority under a chosen representation. Statistical methods flag values far from a centre; Isolation Forest isolates unusual points through random partitions; Local Outlier Factor compares local density with neighbours. One-Class SVM learns a boundary around typical observations.

An anomaly is not necessarily an error, fraud or threat. It may be a valid rare event, a new operating condition or a data-entry problem. Investigate flagged cases and consider the cost of false alarms. Most anomaly methods do not produce calibrated probabilities of wrongdoing.

Scale and feature choice affect distance-based methods. Set expected contamination cautiously. Evaluate with labelled examples if available, but recognise historical labels may be incomplete. Monitor alert rates and the proportion that lead to useful action.

## 2. Worked Python example
Run in VS Code. Install packages with `python -m pip install numpy pandas matplotlib scipy scikit-learn`.

```python
from sklearn.ensemble import IsolationForest
import numpy as np

rng = np.random.default_rng(4)
normal = rng.normal(0, 1, size=(200, 2))
unusual = np.array([[5, 5], [-5, 4], [6, -4]])
X = np.vstack([normal, unusual])
labels = IsolationForest(contamination=.02, random_state=4).fit_predict(X)
print("Flagged:", (labels == -1).sum(), "Last three:", labels[-3:])
```

## 3. Interpretation
Describe the feature representation, model settings and meaning of the output. Validate patterns in original units. Cluster IDs are arbitrary and anomaly flags are not proof of wrongdoing.

## 4. Guided practice
Change contamination and compare flagged counts. Explain why flagged rows need investigation rather than automatic deletion or accusation.

## 5. Independent practice
Apply the method to a dataset. Compare at least two parameter settings or methods, profile results and document stability, limitations and possible actions.

## 6. Knowledge check
1. What structure is the method attempting to discover?
2. Which assumptions are introduced by the representation or distance?
3. How will you assess stability and usefulness?
4. What should not be inferred from the output?

## Lesson summary
Unsupervised algorithms find patterns according to mathematical definitions. Stability, interpretation and practical validation determine whether those patterns deserve to be used.

## Deeper explanation: anomaly scores are investigation priorities

An outlier is unusual relative to a statistical summary or distribution. An anomaly detector operationalises unusualness under a particular representation. An extreme value in one feature may be normal when considered alongside other features, while a contextual anomaly may not be globally extreme.

Isolation Forest repeatedly selects a feature and split value at random. Unusual observations tend to be isolated in fewer splits, producing shorter average path lengths. The contamination setting influences the threshold used to label observations as outliers; it is not a measured probability that a record is bad.

Evaluate an alerting workflow by asking how many records are flagged, how many are data errors or legitimate rare events, the cost of missed cases, investigation capacity and whether the alert rate changes as behaviour shifts. If labels exist, evaluate precision and recall at the chosen threshold. Precision is the fraction of alerts that are relevant; recall is the fraction of relevant cases found.

Keep the original record, model version, score, threshold and review outcome. Route flags to a human process. Do not block customers, accuse people or delete data based only on an anomaly score. Monitor drift and investigate process changes before retraining.

**Practice:** Build an alert-review table with score, flag, original feature values, reviewer outcome and follow-up action. Explain why a flagged case is a lead for investigation, not a verdict.

### Worked example: set a review threshold

An anomaly detector returns a score or label based on its learned notion of normality. A team may only have capacity to review 20 alerts per day. The threshold should therefore be evaluated against review capacity, false-positive cost and the risk of missing a relevant event. Contamination is a modelling assumption or threshold control, not a fraud rate.

If a labelled review sample exists, calculate precision and recall at several thresholds. Also inspect cases the model did not flag, because false negatives matter. If labels are unavailable, sample both flagged and unflagged records for expert review and document the limitations of that process.

Keep an audit trail so decisions can be challenged. The model should prioritise investigation, while a separate evidence-based process determines what action is justified.
