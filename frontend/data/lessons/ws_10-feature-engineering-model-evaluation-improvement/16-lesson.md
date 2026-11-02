# Lesson 16: Threshold Tuning and Cost-Sensitive Decisions

## Learning outcomes

By the end of this lesson, you should be able to Plot ROC and precision-recall curves; calculate ROC AUC and average precision; explain why PR analysis is informative for rare positives; and distinguish ranking from threshold performance.

## 1. Core explanation
A classifier's default threshold of 0.5 is a convention, not a law. The best threshold depends on the costs of false positives and false negatives, the prevalence of the positive class and operational capacity. A lower threshold usually finds more positives but creates more false alarms.

Define a cost matrix before tuning. For each threshold, calculate confusion-matrix counts and expected cost. If review capacity is limited, select a threshold that produces a manageable alert volume. Validate the chosen threshold on separate data and monitor it as prevalence changes.

Threshold tuning does not change the underlying ranking model. It changes how scores become actions. Communicate both the score and the threshold policy. A threshold chosen to maximise F1 may not minimise real business cost.

## 2. Worked Python example
Run in VS Code using the course virtual environment. Install required packages with `python -m pip install numpy pandas scipy matplotlib scikit-learn`.

```python
import numpy as np
from sklearn.metrics import confusion_matrix

y = np.array([0, 0, 0, 1, 1, 1, 0, 1, 0, 1])
p = np.array([.1, .4, .3, .6, .8, .45, .7, .9, .2, .55])
cost_fp, cost_fn = 1, 5
for t in [.25, .4, .5, .65, .8]:
    pred = (p >= t).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    print(t, "FP", fp, "FN", fn, "cost", fp*cost_fp + fn*cost_fn)
```

## 3. Interpretation and safeguards
State the metric, split design and assumptions. Keep preprocessing and feature selection inside the training workflow. Do not use the final test set to tune a threshold, select features or choose hyperparameters.

## 4. Guided practice
Use a cost matrix where a false negative costs five times a false positive. Identify the lowest-cost threshold in this example. Explain why the threshold should be selected on validation data, not final test data.

## 5. Independent practice
Apply the method to a dataset you understand. Record a baseline, define a hypothesis before each change and keep an experiment log. Explain whether any improvement is stable and practically important.

## 6. Knowledge check
1. What question does this method answer?
2. What data leakage risk must be controlled?
3. How does the metric relate to the decision?
4. What evidence would make you trust the improvement?

## Lesson summary
Reliable model improvement requires controlled experiments, leakage-safe preprocessing, a validation design that matches the data and honest reporting of uncertainty.