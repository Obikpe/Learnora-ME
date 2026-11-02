# Lesson 13: Anomaly and Outlier Detection

## Learning outcomes
Explain the unsupervised method, implement the example and judge whether the discovered structure is meaningful.

## 1. Core explanation
Anomaly detection identifies observations that differ from the majority under a chosen representation. Statistical methods may flag values far from a centre; Isolation Forest isolates unusual points through random partitions; Local Outlier Factor compares local density with neighbours. One-Class SVM learns a boundary around typical observations.

An anomaly is not necessarily an error, fraud or threat. It may be a valid rare event, a new operating condition or a data-entry problem. Investigate flagged cases and consider the cost of false alarms. Most anomaly methods do not produce calibrated probabilities of wrongdoing.

Scale and feature choice affect distance-based methods. Set expected contamination cautiously where required. Evaluate with labelled examples if available, but recognise historical labels may be incomplete. For operational use, monitor alert rates and the proportion that lead to useful action.

## 2. Worked Python example
Run in VS Code. Install packages with `python -m pip install numpy pandas matplotlib scipy scikit-learn`.

```python
from sklearn.ensemble import IsolationForest
import numpy as np

rng = np.random.default_rng(4)
normal = rng.normal(0, 1, size=(200, 2))
unusual = np.array([[5, 5], [-5, 4], [6, -4]])
X = np.vstack([normal, unusual])
model = IsolationForest(contamination=.02, random_state=4)
labels = model.fit_predict(X)
print("Flagged:", (labels == -1).sum())
print("Last three flags:", labels[-3:])
```

## 3. Interpretation
Describe the feature representation, model settings and meaning of the output. Validate patterns in original units. Cluster IDs are arbitrary and anomaly flags are not proof of wrongdoing.

## 4. Guided practice
Change contamination and compare the number of flagged cases. Explain why flagged rows need investigation rather than automatic deletion or accusation.

## 5. Independent practice
Apply the method to a dataset. Compare at least two parameter settings or methods, profile results and document stability, limitations and possible actions.

## 6. Knowledge check
1. What structure is the method attempting to discover?
2. Which assumptions are introduced by the representation or distance?
3. How will you assess stability and usefulness?
4. What should not be inferred from the output?

## Lesson summary
Unsupervised algorithms find patterns according to mathematical definitions. Stability, interpretation and practical validation determine whether those patterns deserve to be used.