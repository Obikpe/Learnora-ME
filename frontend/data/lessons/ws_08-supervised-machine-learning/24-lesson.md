# Lesson 24: Model Calibration

## Learning outcomes

By the end of this lesson, you should be able to Explain calibration as agreement between predicted probabilities and observed frequencies; plot a calibration curve; compare calibrated and uncalibrated probabilities; and distinguish calibration from discrimination.


![validation concept diagram](/course-assets/ws08/validation.svg)

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

## 7. Turn the case study into a defensible analysis

An end-to-end project is not a competition to obtain the largest score. It is a documented chain of decisions. Begin by explaining the practical question and why the target is meaningful. Define the observation unit, prediction time and outcome window. Describe where the data came from, who or what it represents, and which populations may be missing. Check whether the target was recorded consistently and whether any feature contains information from after the prediction moment.

Create a baseline before trying a more complex estimator. A baseline reveals how much value the candidate adds beyond a simple reference strategy. Select models and parameters with training and validation data. Keep the final test set separate until the approach is fixed. Choose metrics that reflect the problem: regression errors should be interpreted in target units; classification evaluation should consider class balance, threshold choice and the costs of false positives and false negatives.

## 8. Explain results and limitations

A useful report includes the question, target definition, data description, split design, preprocessing, baseline, model, parameter choices, evaluation results, error analysis and limitations. Include enough detail for another analyst to reproduce the work. Avoid causal language unless the study design supports causal conclusions. A high score on a small or unrepresentative dataset does not guarantee performance on a different population, future period or operational setting.

## 9. Independent project extension

Re-run the project after changing one defensible choice: the split design, feature set, preprocessing, model family or decision threshold. Compare the new result with the original using the same evaluation design. Inspect examples where predictions are wrong and explain what the model appears to struggle with. State what further data or validation would be required before deployment.

## 10. Knowledge check

1. What decision is this model intended to support?
2. How is the target defined and when is the prediction made?
3. Why is the baseline necessary?
4. What does the evaluation metric mean in the original problem's units?
5. Which limitations prevent you from claiming that the result will generalise everywhere?
