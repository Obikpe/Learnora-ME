# Lesson 24: Model Calibration

## Learning outcomes

By the end of this lesson, you should be able to Explain calibration as agreement between predicted probabilities and observed frequencies; plot a calibration curve; compare calibrated and uncalibrated probabilities; and distinguish calibration from discrimination.

## 1. Core explanation
Calibration measures whether predicted probabilities match observed frequencies. Among cases assigned probability around 0.7, a well-calibrated model should be correct about 70% of the time over many comparable cases. Calibration differs from discrimination: a model can rank cases well but produce probabilities that are too extreme or too cautious.

Use a reliability diagram to compare average predicted probability with observed positive frequency in bins. Brier score and log loss assess probability quality, though they also reflect discrimination. Calibration methods include sigmoid scaling and isotonic regression. Fit calibration using validation data or cross-validation, never final test outcomes.

Calibration matters when decisions use risk probabilities or when probabilities are communicated. A calibrated estimate is still uncertain and may become miscalibrated as prevalence or data patterns change.

## 2. Worked Python example
Run in VS Code with the course virtual environment. Install packages with `python -m pip install numpy pandas matplotlib scikit-learn`. Some dataset loaders may require internet access on first use.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV, CalibrationDisplay
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

data = load_breast_cancer(as_frame=True)
Xtr, Xte, ytr, yte = train_test_split(data.data, data.target,
    test_size=.2, random_state=42, stratify=data.target)
base = RandomForestClassifier(n_estimators=150, random_state=42)
calibrated = CalibratedClassifierCV(base, method="sigmoid", cv=5).fit(Xtr, ytr)
CalibrationDisplay.from_estimator(calibrated, Xte, yte, n_bins=8)
plt.show()
```

## 3. Interpretation and checks
Record the target, sample size, split design, metric and model settings. Inspect class-wise results or residuals, not only the headline score. Keep the test set untouched during model selection and report dataset limitations.

## 4. Guided practice
Read the reliability diagram. Identify overconfidence or underconfidence. Explain why calibration should be checked again after deployment.

## 5. Independent practice
Extend the example with another model or evaluation view. Compare candidates using the same training/validation design. Write a short report for a non-technical stakeholder and state what further validation is required.

## 6. Knowledge check
1. What does the method estimate or optimise?
2. Which assumptions and settings affect its behaviour?
3. How could leakage or an inappropriate split inflate performance?
4. What evidence is needed before use?

## Lesson summary
Supervised learning is an evidence-based process: define the target, preserve the prediction timeline, validate fairly, inspect errors and communicate uncertainty.