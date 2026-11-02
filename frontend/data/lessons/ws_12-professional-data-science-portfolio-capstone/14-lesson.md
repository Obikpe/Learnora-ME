# Lesson 14: Evaluation and Error Analysis

## Learning outcomes

By the end of this lesson, you should be able to Evaluate model errors using suitable metrics and representative examples; inspect confusion matrices or residuals; compare relevant groups; and propose proportionate next steps.

## 1. Core explanation
Evaluation should answer whether a model works for its intended use on data it did not train on. Report test-set size, split strategy, baseline and metrics. Then inspect errors: which cases were misclassified, what patterns exist and whether errors are concentrated in a subgroup, time period or feature range.

Avoid only reporting the best metric. For classification, use confusion matrices and class-wise precision/recall. For regression, inspect residual distributions and errors by segment. Check calibration if probabilities guide action. If the test sample is small, explain the uncertainty and avoid overconfident claims.

Error analysis should lead to a specific next step: improve labels, collect more representative data, add a justified feature, change the threshold or stop using the model. Do not keep tuning against the test set.

## 2. Worked example or template
Use the example in VS Code or adapt the structure to your project.

```python
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report

actual = np.array([0, 0, 1, 1, 1, 0, 1, 0, 0, 1])
predicted = np.array([0, 1, 1, 0, 1, 0, 1, 0, 0, 1])
print(confusion_matrix(actual, predicted))
print(classification_report(actual, predicted, zero_division=0))
```

## 3. Professional application
Keep the artefact reproducible and honest. State the data source, time period, methods, your contribution and limitations. Do not publish confidential data or make unsupported performance claims.

## 4. Guided practice
Choose one false positive and one false negative from a project. Explain the operational impact of each and propose a method to investigate whether the error is systematic.

## 5. Independent practice
Create or improve the corresponding project artefact. Ask another person to review it and record any unclear assumptions or missing instructions.

## 6. Knowledge check
1. What decision or audience does this artefact serve?
2. What evidence supports the claim?
3. Which limitations must be disclosed?
4. How can another person verify the work?

## Lesson summary
A professional portfolio demonstrates judgement, evidence, reproducibility and communication—not just familiarity with tools.