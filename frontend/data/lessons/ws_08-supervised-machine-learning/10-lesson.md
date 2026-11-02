# Lesson 10: Classification Thresholds and Probabilities

## Learning outcomes
Explain the technique, implement the worked example, interpret the output and justify when the method is suitable.

## 1. Core explanation
A classifier may output a probability for each class. The threshold converts a probability into a class label. With a threshold of 0.5, a positive class is predicted when its estimated probability is at least 0.5. Lowering the threshold usually increases recall and may reduce precision; raising it usually increases precision and may reduce recall.

The threshold should reflect the decision. In screening, missing a true positive may be costly, so higher recall may be preferred even if more false alarms occur. In an expensive intervention programme, false positives may consume scarce resources, so precision may matter more. The threshold must be selected using validation data, not repeatedly adjusted against the final test set.

A predicted probability is not automatically trustworthy. Calibration asks whether cases assigned probability 0.8 are positive about 80% of the time. Evaluate calibration separately from ranking metrics. Explain that a score is an estimate, not certainty.

## 2. Worked Python example
Run in VS Code using the course virtual environment. Install required packages with `python -m pip install numpy pandas matplotlib scikit-learn`. Some dataset loaders may need internet access on first use.

```python
import numpy as np
from sklearn.metrics import precision_score, recall_score

y_true = np.array([0, 0, 1, 1, 1, 0, 1, 0])
prob = np.array([.1, .4, .45, .55, .8, .2, .7, .6])
for threshold in [.3, .5, .7]:
    pred = (prob >= threshold).astype(int)
    print(threshold, "precision", precision_score(y_true, pred),
          "recall", recall_score(y_true, pred))
```

## 3. Interpretation and checks
Record the target, sample size, split design, metric and model settings. Inspect class-wise results or residuals, not only the headline score. Keep the test set untouched during model selection and report the limitations of the dataset.

## 4. Guided practice
Use the values to compare thresholds 0.3, 0.5 and 0.7. State which threshold you would choose if false negatives cost four times as much as false positives, and explain what other information you need.

## 5. Independent practice
Extend the example with a second model or a different evaluation view. Keep a record of every change and compare candidates using the same training/validation design. Write a short report for a non-technical stakeholder.

## 6. Knowledge check
1. What does this method optimise or estimate?
2. Which assumptions or settings affect its behaviour?
3. How would you detect overfitting or leakage?
4. What evidence is needed before the model is used?

## Lesson summary
Supervised learning is a complete evidence-based process: define the target, preserve the prediction timeline, validate fairly, inspect errors and communicate uncertainty.