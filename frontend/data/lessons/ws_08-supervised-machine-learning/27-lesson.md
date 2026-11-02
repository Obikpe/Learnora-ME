# Lesson 27: End-to-End Classification Case Study

## Learning outcomes

By the end of this lesson, you should be able to Complete a multiclass classification case study; split with stratification; fit a pipeline; inspect class-wise results; and communicate what the small educational dataset cannot establish.

## 1. Core explanation
Build a classification case study around the Wine dataset. Define the target as one of three wine classes, inspect class balance, split with stratification, compare a baseline and candidate, then inspect the confusion matrix and per-class precision and recall. The dataset is educational and small; a high score does not imply performance on commercial wine samples or other populations.

Compare logistic regression with a tree ensemble. Explain scaling requirements and why the algorithms behave differently. Use cross-validation on training data for selection, then one final test evaluation. Inspect which classes are confused and consider whether those errors have equal practical importance.

The report should state data source, target encoding, split, metrics and limitations. Avoid treating the label names as objectively meaningful categories beyond the dataset's definitions.

## 2. Worked Python example
Run in VS Code with the course virtual environment. Install packages with `python -m pip install numpy pandas matplotlib scikit-learn`. The Wine dataset is bundled with scikit-learn, so this example does not need a separate download.

```python
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, classification_report

data = load_wine(as_frame=True)
Xtr, Xte, ytr, yte = train_test_split(data.data, data.target,
    test_size=.25, random_state=11, stratify=data.target)
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000))
model.fit(Xtr, ytr)
pred = model.predict(Xte)
print(confusion_matrix(yte, pred))
print(classification_report(yte, pred, target_names=data.target_names))
```

## 3. Interpretation and checks
Record the target, sample size, split design, metric and model settings. Inspect class-wise results or residuals, not only the headline score. Keep the test set untouched during model selection and report dataset limitations.

## 4. Guided practice
Compare class-wise recall and confusion matrix. Write a stakeholder summary with one strength, one weakness, one dataset limitation and the next validation step.

## 5. Independent practice
Extend the example with another model or evaluation view. Compare candidates using the same training/validation design. Write a short report for a non-technical stakeholder and state what further validation is required.

## 6. Knowledge check
1. What does the method estimate or optimise?
2. Which assumptions and settings affect its behaviour?
3. How could leakage or an inappropriate split inflate performance?
4. What evidence is needed before use?

## Lesson summary
Supervised learning is an evidence-based process: define the target, preserve the prediction timeline, validate fairly, inspect errors and communicate uncertainty.