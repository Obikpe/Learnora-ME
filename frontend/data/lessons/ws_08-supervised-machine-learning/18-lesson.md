# Lesson 18: Handling Imbalanced Classes

## Learning outcomes
Explain the technique, implement the worked example, interpret the output and justify when the method is suitable.

## 1. Core explanation
Class imbalance occurs when one class is much rarer than another. Accuracy can hide poor minority-class detection. Use precision, recall, F1, PR-AUC and confusion matrices according to the decision. Precision-recall curves are often informative when the positive class is rare because they focus on positive predictions.

Possible strategies include class weights, threshold adjustment, under-sampling the majority class and over-sampling the minority class. Apply resampling only inside training folds; resampling before splitting leaks information and changes the test distribution. Synthetic methods such as SMOTE create artificial points and require careful use, especially with mixed categorical and numeric data.

Do not assume that balanced classes are always the goal. The deployment prevalence may be naturally rare. Evaluate on a test set that reflects the real-world class distribution, and report precision and recall at a clearly stated threshold.

## 2. Worked Python example
Run in VS Code using the course virtual environment. Install required packages with `python -m pip install numpy pandas matplotlib scikit-learn`. Some dataset loaders may need internet access on first use.

```python
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from collections import Counter

X, y = make_classification(n_samples=2000, weights=[.95, .05],
                           random_state=12, flip_y=0.01)
Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y,
                                      test_size=.25, random_state=12)
print("Training classes:", Counter(ytr))
for weight in [None, "balanced"]:
    model = LogisticRegression(class_weight=weight, max_iter=1000).fit(Xtr, ytr)
    print("Class weight:", weight)
    print(classification_report(yte, model.predict(Xte), zero_division=0))
```

## 3. Interpretation and checks
Record the target, sample size, split design, metric and model settings. Inspect class-wise results or residuals, not only the headline score. Keep the test set untouched during model selection and report the limitations of the dataset.

## 4. Guided practice
Compare the minority-class recall and precision with and without class weights. Discuss how increased recall may create more false alarms and why the right balance depends on operational costs.

## 5. Independent practice
Extend the example with a second model or a different evaluation view. Keep a record of every change and compare candidates using the same training/validation design. Write a short report for a non-technical stakeholder.

## 6. Knowledge check
1. What does this method optimise or estimate?
2. Which assumptions or settings affect its behaviour?
3. How would you detect overfitting or leakage?
4. What evidence is needed before the model is used?

## Lesson summary
Supervised learning is a complete evidence-based process: define the target, preserve the prediction timeline, validate fairly, inspect errors and communicate uncertainty.