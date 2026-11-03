# Lesson 18: Handling Imbalanced Classes

## Learning outcomes

By the end of this lesson, you should be able to Explain why class imbalance can make accuracy misleading; inspect class proportions; compare class weighting; and evaluate minority-class precision, recall and the operational cost of errors.


![classification concept diagram](/course-assets/ws08/classification.svg)

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

## 7. Understand the model before using it

A model does not understand the world represented by its dataset. It learns a mathematical pattern from the examples it receives. The analyst supplies the meaning by defining what one row represents, which information is available at prediction time and what the target means. Explain these definitions before discussing the algorithm.

Interpret outputs carefully. Probabilities express model estimates, not certainty. Feature importance describes how a model uses information, not necessarily causal influence. Evaluation metrics summarise selected errors, not every consequence of using a model. Always connect the result to the decision and the population where it will be applied.

## 8. Build a fair and repeatable experiment

Check data types, missingness, duplicates, unusual values and target distribution. Choose a split that matches deployment: chronological for future prediction, group-aware when people or entities appear repeatedly, and stratified when preserving class proportions is important. Fit imputers, encoders and scalers on training data only. A pipeline helps ensure the same fitted transformations are applied to validation, test and future data.

Start with a baseline. Select model settings using validation data or cross-validation, then evaluate the chosen approach on a held-out test set once. Keep a record of feature definitions, random seeds, package versions, split strategy and parameter values. If the data changes, investigate whether the target definition, population or collection process also changed.

## 9. Worked reasoning example

Imagine predicting whether a learner will need additional support. Define a snapshot date, an outcome window and the intervention. Use only activity recorded before the snapshot. If the same learner appears in several rows, random splitting may put that learner in both training and test sets, making the test easier than the real task. Consider a group-based or time-based split. Inspect not only the average score but also who receives false alerts and who is missed.

## 10. Self-study and independent practice

Explain the method from memory: its purpose, required inputs, learning mechanism, an important setting, one failure mode and an appropriate evaluation strategy. Apply it to a documented dataset and produce a notebook with a precise question, data-quality checks, split rationale, baseline, candidate model, interpreted metrics, error analysis and limitations. Explain why each decision was made.

Do not remove rare observations only because they make performance worse. Determine whether they are errors, valid rare cases or evidence that the method does not work well for an important part of the population.

## 11. Knowledge check

1. What does the method learn from training examples?
2. What assumptions and parameter choices influence its behaviour?
3. What could make an evaluation result misleading?
4. How would you inspect errors beyond a single summary metric?
5. What further validation is needed before using the model in practice?
