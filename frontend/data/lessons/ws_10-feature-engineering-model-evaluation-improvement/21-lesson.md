# Lesson 21: Learning Curves and Error Diagnosis

## Learning outcomes
Read learning curves; distinguish training and validation behaviour; diagnose common error patterns; inspect residuals and misclassified cases; and propose evidence-based next experiments.

## 1. What a learning curve shows
A learning curve plots model performance against the amount of training data. It commonly shows training score and validation score as the training sample size increases. The gap and direction of the curves help diagnose whether the model may benefit from more data or a different level of complexity.

If both scores are poor and close together, the model may have high bias or inadequate features. If training is strong but validation is weaker, variance or distribution mismatch may be present. If validation performance continues to improve as more data is added, collecting more representative data may help.

## 2. Error diagnosis
Do not stop at one aggregate metric. For regression, inspect residuals against predictions, time and relevant groups. For classification, inspect false positives and false negatives, confidence scores and subgroup performance. Ask whether errors cluster around a particular range, category, period or population.

A model can have a reasonable overall score but fail for a group that matters. Error analysis can reveal missing features, data-quality issues, label ambiguity or a mismatch between the training data and deployment.

![Learning curve patterns](/course-assets/ws10/learning-curves.svg)

## 3. Worked example
```python
import matplotlib.pyplot as plt
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import learning_curve, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import numpy as np

X, y = load_breast_cancer(return_X_y=True)
model = make_pipeline(
    StandardScaler(),
    LogisticRegression(max_iter=3000)
)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
sizes, train_scores, valid_scores = learning_curve(
    model, X, y, cv=cv, scoring="accuracy",
    train_sizes=np.linspace(0.1, 1.0, 8), n_jobs=-1
)

plt.plot(sizes, train_scores.mean(axis=1), marker="o", label="Training")
plt.plot(sizes, valid_scores.mean(axis=1), marker="o", label="Validation")
plt.xlabel("Training examples")
plt.ylabel("Accuracy")
plt.legend()
plt.title("Learning curve")
plt.show()
```

The pipeline scales inside each fold. The plot shows how the average scores change with training size. Inspect the shape rather than seeking a universal numerical gap threshold. Small datasets can produce noisy curves.

## 4. A disciplined diagnosis loop
1. Verify the split and check leakage.
2. Confirm labels and feature definitions.
3. Compare train and validation performance.
4. Inspect error examples and subgroups.
5. Form one hypothesis about the failure.
6. Make one controlled change.
7. Repeat the same validation design.
8. Record whether the evidence supports the hypothesis.

This prevents random experimentation and makes improvements explainable.

## 5. Common mistakes
- Treating a learning curve as proof that more data will solve every problem.
- Inspecting errors only for the overall majority group.
- Changing several things at once.
- Ignoring label quality.
- Diagnosing overfitting before checking split leakage.
- Reporting a learning curve without describing its cross-validation method.

## Guided practice
A learning curve shows near-perfect training accuracy and slowly rising validation accuracy. Suggest two possible causes and two tests that would distinguish them.

## Independent practice
Generate a learning curve for a model. Then inspect the ten largest regression errors or a sample of false positives and false negatives. Group errors by a relevant feature and propose one improvement.

## Knowledge check
1. What do learning curves plot?
2. What might a large train/validation gap suggest?
3. What might low, similar scores suggest?
4. Why inspect errors by subgroup?
5. Why change one thing at a time?

## Lesson summary
Learning curves show how performance changes with data volume, while error analysis shows where predictions fail. Combine both with leakage checks and controlled experiments to choose the next improvement.

## 6. Deeper reasoning: error analysis turns a score into a hypothesis

A learning curve helps describe whether performance changes with more training data, but it cannot tell you exactly why individual predictions fail. That is the purpose of error analysis. Start by examining a sample of the largest errors or the false positives and false negatives. Look for common properties: a particular region, customer type, time period, product category or range of the target. These patterns can suggest missing features, inconsistent data collection or an unsuitable model assumption.

Avoid selecting only the most interesting failures. Use a reproducible sampling method, such as the largest absolute regression errors plus a random sample of ordinary errors. For classification, inspect both false positives and false negatives. If you only study cases the model got wrong in one direction, you may miss a different failure mode.

Subgroup analysis needs enough observations to be meaningful. A subgroup with three examples can show a concerning pattern, but its metric will be highly uncertain. Report support counts and avoid making broad claims from tiny groups. Consider whether subgroup differences reflect real behaviour, data quality, different label definitions or historical bias in the data.

Translate each finding into a testable hypothesis. For example: “Delivery predictions are less accurate for rural locations because distance is represented as a straight-line measure rather than road travel time.” Then propose one feature or data improvement and evaluate it using the same validation design. This turns error inspection into a disciplined improvement cycle rather than a collection of anecdotes.