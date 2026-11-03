# Lesson 17: Threshold Tuning and Cost-Sensitive Decisions

## Learning outcomes
Explain how a classification threshold changes predictions; choose a threshold using validation data; calculate a simple cost function; and distinguish model ranking from operational decision-making.

## 1. A threshold turns scores into actions
A classifier may return an estimated probability or decision score. A threshold determines which observations are flagged positive. A lower threshold usually increases recall because more cases are flagged, but it may also reduce precision by increasing false positives. A higher threshold usually reduces the number of alerts but can miss more true positives.

There is no universally correct threshold of 0.5. The threshold should be selected in the context of the decision. A fraud team may prefer to review more transactions if the cost of missed fraud is high. A limited medical follow-up service may need a threshold that balances missed cases against scarce capacity.

## 2. Cost-sensitive decisions
A simple expected cost can be written as:

`Total cost = FP × cost_FP + FN × cost_FN`

This is a simplification: real costs may vary by case and include investigation time, customer friction, regulatory consequences and downstream outcomes. Still, it makes an important point: false positives and false negatives may not have equal consequences.

A model with the highest F1 may not minimise operational cost. A threshold that produces too many alerts may be unusable even if recall is high.

![Threshold trade-off](/course-assets/ws10/threshold-tradeoff.svg)

## 3. Tune on validation data
Use predicted probabilities from a model fitted on training data. Evaluate candidate thresholds on a validation set or out-of-fold predictions. Choose a threshold according to an explicit objective or capacity constraint. Keep the final test set untouched until the threshold and workflow are fixed.

## 4. Worked example
```python
import numpy as np
from sklearn.metrics import confusion_matrix, precision_score, recall_score

y_true = np.array([1, 0, 0, 1, 0, 1, 0, 0, 1, 0])
probabilities = np.array([.82, .61, .40, .55, .20, .72, .48, .12, .36, .08])

cost_fp = 2
cost_fn = 10

for threshold in [0.2, 0.35, 0.5, 0.65, 0.8]:
    prediction = (probabilities >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(
        y_true, prediction, labels=[0, 1]
    ).ravel()
    cost = fp * cost_fp + fn * cost_fn
    print({
        "threshold": threshold,
        "precision": round(precision_score(y_true, prediction, zero_division=0), 2),
        "recall": round(recall_score(y_true, prediction, zero_division=0), 2),
        "false_positives": fp,
        "false_negatives": fn,
        "illustrative_cost": cost
    })
```

The costs are invented for teaching. Change them to represent the actual decision context. The threshold with the lowest cost on this tiny sample is not automatically a reliable policy; the estimate is noisy and must be tested on sufficient validation data.

## 5. Capacity constraints
Sometimes the team can review only 200 cases per day. Instead of choosing a threshold solely by a metric, select the top-scoring 200 cases or choose a threshold that respects the review capacity. Monitor how the number of alerts changes over time. If the score distribution shifts, a fixed threshold may produce a very different workload.

## 6. Probability calibration
Threshold decisions depend on scores. If a model predicts 0.8 for 100 cases, calibration asks whether roughly 80 of those cases are positive over repeated comparable groups. A well-ranked model is not necessarily well-calibrated. Calibration methods should be fitted using training/validation procedures, not the final test set.

## Common mistakes
- Assuming 0.5 is always the best threshold.
- Selecting a threshold on test labels.
- Optimising F1 when the real objective is cost or capacity.
- Ignoring the number of alerts.
- Treating uncalibrated scores as reliable probabilities.
- Changing the threshold without monitoring operational impact.

## Guided practice
A fraud team estimates a false negative costs ₦50,000 and a false positive costs ₦500 in review time. Explain why recall may be prioritised, then identify why an extremely low threshold could still be harmful.

## Independent practice
Use validation predictions to compare thresholds. Report precision, recall, confusion matrix, alert volume and a cost calculation. State the assumed costs and show how the preferred threshold changes if those assumptions change.

## Knowledge check
1. What does lowering a threshold usually do to recall?
2. Why may the best F1 threshold not minimise business cost?
3. Which data should be used to select the threshold?
4. How can review capacity affect threshold choice?
5. What is calibration?

## Lesson summary
Threshold selection converts model scores into operational actions. Select it with validation evidence and an explicit cost or capacity objective, then protect the test set for final evaluation.

## 7. Deeper reasoning: threshold choice is a policy decision

A threshold determines which observations receive an action. That action might be an alert, a manual review, a customer call or an automatic block. The threshold therefore connects statistical output to an operational policy. Before selecting it, identify who bears the cost of each error and what happens after a positive prediction. A false positive that triggers a quick manual check has a different cost from one that automatically freezes an account.

The simple cost formula in this lesson assumes every false positive has the same cost and every false negative has the same cost. Real cases may differ. A high-value transaction may have a different expected loss from a low-value one. A review may take longer for some case types. A more advanced decision process can estimate expected cost per observation, but it still requires reliable assumptions and careful validation.

Thresholds can also drift operationally. If the model is unchanged but the incoming population changes, the proportion of scores above a fixed threshold can increase. The review team may suddenly receive too many alerts. Monitor alert volume, precision where labels become available, false-negative estimates and score distributions. A threshold should be revisited through a documented governance process, not adjusted informally whenever workload becomes uncomfortable.

Finally, do not assume that lowering the threshold always improves the business outcome. It usually increases recall on a fixed ranked set, but it may flood the team with false positives, delay investigation and reduce attention to the most serious cases. Evaluate the complete process, including human capacity and downstream consequences.