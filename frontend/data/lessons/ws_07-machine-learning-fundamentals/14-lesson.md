# Lesson 14: Baseline Models and Evaluation

## Learning outcomes
Explain why a baseline is essential; build DummyClassifier and DummyRegressor models; choose suitable classification and regression metrics; interpret a confusion matrix; and communicate performance with limitations.

## 1. What is a baseline?
A baseline is a simple reference that a more sophisticated model should improve upon. It answers: how well could we do without learning a complex relationship?

For classification, a majority-class baseline predicts the most common class. For regression, a baseline may predict the training mean or median. In a business setting, the existing manual process or a simple business rule may be a more meaningful baseline.

If a complex model barely improves on the baseline, its extra cost, maintenance and risk may not be justified.

## 2. Classification confusion matrix
A confusion matrix compares actual classes with predicted classes. For binary classification:
- True positive (TP): actual positive, predicted positive.
- True negative (TN): actual negative, predicted negative.
- False positive (FP): actual negative, predicted positive.
- False negative (FN): actual positive, predicted negative.

![Confusion matrix](/course-assets/ws07/14-confusion-matrix.svg)

A false positive and a false negative can have very different consequences. In a fraud screening workflow, false positives may inconvenience legitimate customers; false negatives may allow fraud to go undetected.

## 3. Core classification metrics
\[
Accuracy=\frac{TP+TN}{TP+TN+FP+FN}
\]
Accuracy is the fraction of correct predictions. It can be misleading when one class is rare.

\[
Precision=\frac{TP}{TP+FP}
\]
Precision asks: of the cases predicted positive, how many were actually positive?

\[
Recall=\frac{TP}{TP+FN}
\]
Recall asks: of all actual positive cases, how many did we detect?

\[
F1=2\times\frac{Precision\times Recall}{Precision+Recall}
\]
F1 is the harmonic mean of precision and recall. It is useful when both matter, but it ignores true negatives and may not reflect every operational cost.

Specificity = TN/(TN+FP), the proportion of actual negatives correctly identified. Balanced accuracy averages recall across classes.

## 4. Calculate metrics with scikit-learn
```python
from sklearn.metrics import (
    confusion_matrix, classification_report,
    accuracy_score, precision_score, recall_score, f1_score
)

y_true = [1, 1, 1, 0, 0, 0, 0, 1]
y_pred = [1, 0, 1, 0, 1, 0, 0, 1]

print(confusion_matrix(y_true, y_pred))
print("Accuracy:", accuracy_score(y_true, y_pred))
print("Precision:", precision_score(y_true, y_pred))
print("Recall:", recall_score(y_true, y_pred))
print("F1:", f1_score(y_true, y_pred))
print(classification_report(y_true, y_pred, zero_division=0))
```

The order of labels in a confusion matrix should be checked, especially when labels are not 0 and 1. classification_report provides per-class precision, recall and F1 plus summary averages.

## 5. Thresholds and probabilities
Many classifiers produce a probability score. The default class decision often uses a threshold of 0.5, but this is not a universal law. Lowering the threshold may increase recall and also increase false positives. Raising it may increase precision while missing more positive cases.

Choose a threshold using validation data and the actual costs of mistakes. Do not select it by looking repeatedly at the final test results.

## 6. ROC-AUC and precision-recall
ROC curves compare true-positive rate with false-positive rate across thresholds. ROC-AUC measures ranking ability across thresholds. In highly imbalanced problems, precision-recall curves can be more informative because they focus on positive predictions and detection. Neither metric alone determines whether a model is operationally useful.

## 7. Regression metrics
- MAE: average absolute error in target units.
- MSE: average squared error, with greater penalty for large misses.
- RMSE: square root of MSE, in target units.
- R-squared: compares model squared error with a mean-prediction reference under the usual definition. It can be negative on test data if the model performs worse than that reference.

```python
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
actual = [100, 120, 150, 180]
predicted = [110, 115, 160, 210]
print("MAE:", mean_absolute_error(actual, predicted))
print("RMSE:", mean_squared_error(actual, predicted) ** 0.5)
print("R2:", r2_score(actual, predicted))
```

## 8. Compare with a baseline fairly
```python
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

data = load_diabetes(as_frame=True)
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.2, random_state=42
)
models = {
    "Median baseline": DummyRegressor(strategy="median"),
    "Random forest": RandomForestRegressor(n_estimators=100, random_state=42)
}
for name, model in models.items():
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    print(name, "MAE:", mean_absolute_error(y_test, pred))
```

Both models use the same split and metric, so their results can be compared more fairly. The random forest is not automatically preferable: consider improvement size, uncertainty, interpretability, latency and maintenance.

## 9. Communicate an evaluation
A useful report states:
- what was predicted and for whom;
- what data and split were used;
- the number of test examples;
- baseline and candidate results;
- metrics and their meaning;
- important error patterns;
- limitations and recommended next steps.

Avoid saying "the model is 95% accurate" without describing the sample, target, split and error costs.

## Common mistakes
- Using accuracy for a rare positive class without further analysis.
- Confusing precision with recall.
- Reporting a metric without its definition.
- Comparing models on different test sets.
- Ignoring the baseline.
- Choosing a threshold on the test set.

## Guided practice
Use the provided labels and predictions to calculate TP, TN, FP and FN by hand. Verify with confusion_matrix. Explain which error type would be most costly for a fraud alert system and why the answer depends on the workflow.

## Independent practice
Build a baseline and one candidate model for a classification or regression dataset. Choose at least two metrics, explain why they matter and prepare a one-page evaluation report.

## Knowledge check
1. Why do we need a baseline?
2. What does precision measure?
3. What does recall measure?
4. Why can a threshold change error rates?
5. What does negative test R-squared indicate?

## Lesson summary
Evaluation is more than a score. Baselines, error types, suitable metrics and clear communication show whether a model adds value for the intended task.