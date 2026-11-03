# Lesson 16: Precision-Recall and ROC Analysis

## Learning outcomes
Explain score thresholds; interpret ROC and precision-recall curves; calculate AUC; understand why PR curves are valuable for rare positives; and avoid treating a curve summary as a complete decision.

## 1. Scores are not labels
Many classifiers produce a score or estimated probability. A threshold converts that score into a class. If the threshold is 0.5, scores at or above 0.5 may be labelled positive. Changing the threshold changes the number of predicted positives and therefore changes precision and recall.

A threshold is a decision rule, not a property that nature supplies. It should reflect the cost of false positives, false negatives, review capacity and the reliability of the model's probabilities.

## 2. ROC curve
The Receiver Operating Characteristic (ROC) curve plots true positive rate (recall) against false positive rate at different thresholds. False positive rate is FP / (FP + TN). A curve closer to the top-left generally indicates better separation.

ROC-AUC summarises ranking performance across thresholds. An AUC of 0.5 is approximately random ranking; 1.0 is perfect ranking. AUC does not tell you whether probabilities are calibrated or whether a chosen threshold meets business needs.

## 3. Precision-recall curve
A precision-recall (PR) curve plots precision against recall at different thresholds. It focuses on positive-class performance and is particularly informative when positives are rare. The baseline precision for a random ranking is related to the positive prevalence.

ROC can look strong in a highly imbalanced dataset because the false-positive rate denominator includes many negatives. A PR curve makes the trade-off in positive predictions more visible.

![ROC and PR curves](/course-assets/ws10/roc-pr-curves.svg)

## 4. Worked example
```python
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score, average_precision_score,
    RocCurveDisplay, PrecisionRecallDisplay
)
import matplotlib.pyplot as plt

X, y = make_classification(
    n_samples=1200, n_features=12, weights=[0.94, 0.06],
    random_state=42
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42
)
model = LogisticRegression(max_iter=2000)
model.fit(X_train, y_train)
scores = model.predict_proba(X_test)[:, 1]

print("ROC-AUC:", roc_auc_score(y_test, scores))
print("Average precision:", average_precision_score(y_test, scores))

RocCurveDisplay.from_predictions(y_test, scores)
plt.show()
PrecisionRecallDisplay.from_predictions(y_test, scores)
plt.show()
```

The model returns two class probabilities per row; selecting column 1 obtains the score for the positive class. ROC-AUC and average precision evaluate ranking over thresholds. The plots should be read alongside class prevalence and the operating threshold.

## 5. AUC limitations
AUC can conceal poor performance in the threshold region that matters operationally. A model can rank cases well but produce poorly calibrated probabilities. ROC-AUC does not tell you how many cases an investigation team must review. Average precision and PR curves are often more informative for rare positives, but they also do not select the final threshold for you.

## 6. Common mistakes
- Passing hard class labels to AUC instead of continuous scores.
- Comparing PR curves without reporting positive prevalence.
- Assuming AUC is the percentage of predictions that are correct.
- Choosing a threshold using the final test labels.
- Ignoring calibration and operational capacity.
- Treating ROC-AUC as sufficient for rare-event detection.

## Guided practice
A fraud model has ROC-AUC 0.96 but average precision 0.35 when fraud prevalence is 2%. Explain why the two figures can coexist and why the baseline matters.

## Independent practice
Train a classifier on imbalanced data. Plot ROC and PR curves, report ROC-AUC and average precision, and identify a threshold range worth investigating. Do not use the test set repeatedly to choose that threshold.

## Knowledge check
1. What does the threshold control?
2. What does the ROC curve plot?
3. Why can PR analysis be useful with rare positives?
4. Why should continuous scores be used for AUC?
5. What does AUC not tell you about probability calibration?

## Lesson summary
ROC and PR curves evaluate ranking across thresholds. They are useful summaries, but the final operating point must be chosen using validation evidence, class prevalence and the consequences of each error.