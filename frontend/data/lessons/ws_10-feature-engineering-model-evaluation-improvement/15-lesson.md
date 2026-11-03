# Lesson 15: Classification Evaluation Metrics

## Learning outcomes
Interpret a confusion matrix; calculate accuracy, precision, recall and F1; explain class imbalance; and select metrics according to the costs of false positives and false negatives.

## 1. Classification decisions
A classifier assigns a class, such as fraud/not fraud or churn/not churn. To evaluate it, compare predicted labels with actual labels. For binary classification, the four outcomes are:
- True positive (TP): positive case correctly predicted positive.
- True negative (TN): negative case correctly predicted negative.
- False positive (FP): negative case incorrectly predicted positive.
- False negative (FN): positive case incorrectly predicted negative.

The meaning of positive must be stated. In fraud detection, fraud may be positive; in a medical screening task, disease may be positive.

## 2. Confusion matrix
A confusion matrix counts the four outcomes. It makes the types of error visible rather than compressing them into one score.

**Accuracy** is (TP + TN) / all observations. It is useful when classes and error costs are reasonably balanced, but can be misleading with rare positives.

**Precision** is TP / (TP + FP). Of the cases predicted positive, what proportion were truly positive?

**Recall (sensitivity)** is TP / (TP + FN). Of all actual positives, what proportion did the model find?

**Specificity** is TN / (TN + FP). Of all actual negatives, what proportion did it correctly reject?

**F1** is the harmonic mean of precision and recall. It balances the two but does not include true negatives and assumes a particular trade-off.

![Confusion matrix](/course-assets/ws10/confusion-matrix.svg)

## 3. Worked example
```python
from sklearn.metrics import (
    confusion_matrix, classification_report,
    accuracy_score, precision_score, recall_score, f1_score
)

actual = [1, 1, 1, 0, 0, 0, 0, 1, 0, 0]
predicted = [1, 0, 1, 0, 1, 0, 0, 0, 0, 0]

print(confusion_matrix(actual, predicted, labels=[0, 1]))
print("Accuracy:", accuracy_score(actual, predicted))
print("Precision:", precision_score(actual, predicted, zero_division=0))
print("Recall:", recall_score(actual, predicted, zero_division=0))
print("F1:", f1_score(actual, predicted, zero_division=0))
print(classification_report(actual, predicted, zero_division=0))
```

The example includes false negatives: some actual positives were missed. In a fraud workflow, missing a fraudulent transaction may be costly. In a review workflow, too many false positives may overwhelm investigators. The correct metric depends on the operational consequence.

## 4. Class imbalance
Suppose only 1% of transactions are fraudulent. A model that predicts "not fraud" for every transaction has 99% accuracy but detects no fraud. Accuracy alone is therefore inadequate.

Use precision, recall, F1, balanced accuracy, PR-AUC or other task-appropriate metrics. Always compare against a simple baseline and inspect the confusion matrix. If the classes are imbalanced, ensure folds contain suitable representation and report support counts.

## 5. Macro, micro and weighted averages
For multiclass classification, averaging choices matter. Macro average computes a metric per class and gives each class equal weight. Weighted average weights by class support. Micro average aggregates contributions across classes before calculating the metric. The choice should match whether every class matters equally or common classes dominate the operational workload.

## 6. Common mistakes
- Reporting accuracy alone on imbalanced data.
- Failing to define the positive class.
- Confusing precision with recall.
- Comparing weighted and macro F1 as if they were identical.
- Ignoring support counts for rare classes.
- Treating a classifier's label as a probability.

## Guided practice
A screening model finds 80 of 100 positive cases but flags 200 negative cases as positive. Calculate recall and explain why precision requires the total number of predicted positives.

## Independent practice
Train a classifier on an imbalanced dataset. Report the confusion matrix, precision, recall, F1 and balanced accuracy. Compare with a majority-class baseline and explain which error matters most in the intended application.

## Knowledge check
1. What is a false positive?
2. What does precision answer?
3. What does recall answer?
4. Why can accuracy be misleading?
5. What is the difference between macro and weighted averages?

## Lesson summary
Classification evaluation must expose the kinds of mistakes a model makes. Define the positive class, inspect the confusion matrix and choose metrics according to class balance and the real cost of errors.

## 7. Deeper reasoning: the positive class and the decision context matter

Precision and recall are not abstract properties detached from the task. They describe different consequences. In a fraud-screening system, a false negative is a fraudulent transaction that was not flagged; a false positive is a legitimate transaction sent for review. In a disease-screening context, a false negative may mean a person who needs follow-up is missed, while a false positive may cause additional testing and anxiety. The preferred balance depends on the context and must involve the people responsible for the decision.

Class imbalance changes how useful accuracy is. If only 2 out of 1,000 cases are positive, predicting negative every time gives 99.8% accuracy but zero recall for the positive class. A baseline should therefore be chosen thoughtfully. Compare the model against simple strategies and report how many positive cases were available in the test set.

For multiclass classification, macro and weighted averages answer different questions. Macro averaging gives every class equal weight, which can expose poor performance on a rare class. Weighted averaging reflects class support, so common classes dominate the result. If a rare class is especially important, weighted F1 can conceal its weakness. Report per-class precision, recall and support where the consequences differ.

Also distinguish the predicted label from the model's score. A class label is the result after a threshold has been applied. Precision and recall at one threshold do not describe ranking performance across all thresholds. Use probability or decision scores for curve analysis, and state the threshold used for the confusion matrix.