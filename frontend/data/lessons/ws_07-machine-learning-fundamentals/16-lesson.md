# Lesson 16: A Complete First ML Project

## Learning outcomes
Explain the method, implement the example in Python, interpret its result, and identify risks that could invalidate the conclusion.

## 1. Concepts and reasoning
This lesson brings the workflow together using a familiar, small classification problem. A complete project states the decision, target, unit of observation, available features, data source, split method, baseline, candidate model, metric, error analysis and limitations. The notebook or script should be reproducible from a clean environment.

The example uses the breast cancer dataset bundled with scikit-learn. The target is a dataset label, not a diagnosis for a real person. Do not use this educational demonstration for clinical decisions. The model is trained and evaluated on a held-out split. Accuracy is included for demonstration, but a real risk-sensitive task should inspect sensitivity, specificity, confusion matrix, calibration and consequences of errors.

The final report should not say merely “the model is accurate”. State the test-set size, metric, baseline comparison and important limitations. A good first project demonstrates a responsible process, not just a high score.

## 2. Worked example
Run in VS Code in your course virtual environment. Install packages as required: `python -m pip install numpy pandas scikit-learn matplotlib`.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix

data = load_breast_cancer(as_frame=True)
X, y = data.data, data.target
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
baseline = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
model.fit(X_train, y_train)
print("Baseline accuracy:", baseline.score(X_test, y_test))
print("Model accuracy:", model.score(X_test, y_test))
print(confusion_matrix(y_test, model.predict(X_test)))
print(classification_report(y_test, model.predict(X_test),
                            target_names=data.target_names))
```

## 3. Interpretation
State what was learned from training data and what was measured on unseen data. Check whether the metric answers the real decision question. A technically correct output can still be misleading if the target, split or population is wrong.

## 4. Guided practice
Write a one-page report with: problem definition, dataset and target, split strategy, baseline result, model result, confusion matrix interpretation, at least two limitations and a recommendation about whether further validation is required. Do not describe this educational model as suitable for diagnosis.

## 5. Independent practice
Apply the lesson to a small dataset. Record the source, unit of observation, target and feature availability. Save your code and a short report that includes evidence, limitations and the next validation step.

## 6. Knowledge check
1. What assumption is most important in this method?
2. What is the difference between training performance and generalisation?
3. How could leakage or sampling bias affect the result?
4. What would you tell a stakeholder before they use the model?

## Lesson summary
A trustworthy ML workflow is reproducible, uses a suitable baseline and evaluation design, and communicates errors and limitations as carefully as headline performance.