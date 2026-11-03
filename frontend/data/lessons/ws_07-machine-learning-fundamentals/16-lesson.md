# Lesson 16: A Complete First Machine Learning Project

## Learning outcomes
Complete a small supervised-learning project; frame a prediction problem; inspect and split data; build a preprocessing pipeline; compare a baseline with a candidate model; evaluate errors; and present a reproducible report with limitations.

![End-to-end machine-learning project](/course-assets/ws07/16-project-workflow.svg)

## 1. Project brief
In this capstone, you will build an educational classification model using the breast cancer dataset included with scikit-learn. The dataset contains measurements associated with digitised images of breast masses and a target label. This is an educational exercise only. It is not a diagnostic tool, must not be used for clinical decisions and does not establish that a model is safe for healthcare.

The project demonstrates a workflow, not a real deployment. Your task is to predict the dataset's provided label using the numeric features, then evaluate the model honestly.

## 2. Project questions
- What is one row?
- What does the target label represent in this bundled dataset?
- Which features are available?
- How many examples and features are present?
- What baseline can we establish?
- Does a model improve on that baseline?
- What kinds of mistakes does it make?
- What are the limits of this evaluation?

## 3. Set up the project
Suggested folder structure:
```text
ws07-first-ml-project/
├── data/                 # only if using an external dataset
├── notebooks/
│   └── exploration.ipynb
├── src/
│   └── train.py
├── reports/
│   └── project-report.md
├── requirements.txt
└── README.md
```

Install:
```bash
python -m pip install numpy pandas matplotlib scikit-learn
python -m pip freeze > requirements.txt
```

## 4. Load and inspect the data
```python
import pandas as pd
from sklearn.datasets import load_breast_cancer

dataset = load_breast_cancer(as_frame=True)
X = dataset.data
y = dataset.target

print("Feature shape:", X.shape)
print("Target shape:", y.shape)
print(X.head())
print(X.info())
print(y.value_counts())
print(y.value_counts(normalize=True))
```

X contains the numerical input features; y contains the target labels. Inspect target_names to understand how integer labels map to the dataset's class names. Do not assume that 1 always means the positive condition in every dataset.

## 5. Define a baseline
A majority-class baseline predicts the most frequent training class. It gives a reference score. A model that does not outperform this baseline in a meaningful way may not be useful.

## 6. Split the data
```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(X_train.shape, X_test.shape)
```
The test set is held back for final evaluation. Do not use it repeatedly to select settings. For a real deployment, the split must represent the intended future population and time period.

## 7. Build baseline and candidate pipelines
```python
from sklearn.dummy import DummyClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

baseline = DummyClassifier(strategy="most_frequent")
baseline.fit(X_train, y_train)

model = make_pipeline(
    StandardScaler(),
    LogisticRegression(max_iter=2000)
)
model.fit(X_train, y_train)
```

The baseline learns the most frequent class in training data. StandardScaler learns means and standard deviations from training data. LogisticRegression learns coefficients to estimate class probabilities. The pipeline ensures that the scaler is fitted only on training rows and reused for test rows.

## 8. Evaluate the held-out data
```python
from sklearn.metrics import (
    accuracy_score, confusion_matrix,
    classification_report, roc_auc_score
)

baseline_pred = baseline.predict(X_test)
predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)[:, 1]

print("Baseline accuracy:", accuracy_score(y_test, baseline_pred))
print("Model accuracy:", accuracy_score(y_test, predictions))
print("Confusion matrix:\n", confusion_matrix(y_test, predictions))
print(classification_report(
    y_test, predictions, target_names=dataset.target_names
))
print("ROC-AUC:", roc_auc_score(y_test, probabilities))
```

predict() returns class labels. predict_proba() returns estimated class probabilities; [:, 1] selects the estimated probability for class label 1. ROC-AUC measures ranking across thresholds, not clinical usefulness. Always verify which class is represented by label 1 before interpreting it.

## 9. Interpret the confusion matrix
Use the label order to identify true negatives, false positives, false negatives and true positives. In this dataset, understand the class-name mapping before deciding which error is more serious. In a real medical context, error costs, clinical pathways, prevalence, calibration, external validation and professional oversight would all matter. This classroom model is not suitable for diagnosis.

## 10. Inspect model limitations
Your report should state:
- this is a bundled educational dataset, not a representative current clinical sample;
- a single random split produces one estimate and may vary with the split;
- there is no external validation in this exercise;
- performance may change across hospitals, populations, devices and measurement processes;
- metrics do not establish clinical benefit, fairness or safety;
- the exercise does not authorise real-world use.

## 11. Final report template
### Problem and intended use
State the educational prediction task and clearly exclude clinical use.

### Data
Describe source, rows, features, target definition and class balance.

### Method
Describe split, baseline, pipeline, estimator and any settings.

### Results
Report baseline and model metrics, confusion matrix and test sample size.

### Interpretation
Explain the errors and what they mean for this limited exercise.

### Limitations
State at least three limitations and what further evidence would be required.

### Conclusion
Say whether the candidate improved on the baseline and whether that evidence is enough for deployment. For this educational dataset, the answer should explicitly be no.

## 12. Assessment rubric
| Area | Evidence | Weight |
|---|---|---:|
| Problem framing | Clear unit, target and intended use | 15% |
| Data understanding | Correct inspection and label interpretation | 15% |
| Leakage prevention | Correct split and pipeline | 20% |
| Evaluation | Baseline, suitable metrics and confusion matrix | 20% |
| Interpretation | Accurate explanation of errors | 15% |
| Reproducibility and ethics | Requirements, limitations and no clinical claims | 15% |

## Independent extension
Repeat the project with a different non-sensitive public dataset. Choose a prediction problem with a clear target and appropriate permission. Document the source, prediction time, split strategy, baseline, candidate, metrics and limitations. Do not choose a high-stakes application for an unsupervised beginner project.

## Final knowledge check
1. Why do we establish a baseline?
2. Why is scaling inside a pipeline?
3. What does stratify=y do?
4. What does the confusion matrix reveal?
5. Why does a strong test score not prove deployment readiness?

## Course completion
You have now worked through the foundations of ML, learning paradigms, project workflow, data representation, mathematical ideas, Python tooling, EDA, preprocessing, data splitting, loss functions, generalisation, evaluation and responsible use.

A good beginner ML project is not one that merely produces a high score. It is one where the question is clear, the data is understood, leakage is controlled, the baseline is fair, the evaluation is meaningful and the limitations are honestly communicated.