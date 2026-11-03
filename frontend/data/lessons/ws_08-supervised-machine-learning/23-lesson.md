# Lesson 23: Multi-Class Classification

## Learning outcomes

By the end of this lesson, you should be able to Train and evaluate a multiclass classifier; read a multiclass confusion matrix; report per-class precision and recall; and explain macro, micro and weighted averaging.


![validation concept diagram](/course-assets/ws08/validation.svg)

## 1. Core explanation
Multiclass classification predicts one of more than two mutually exclusive classes. One-vs-rest trains a binary classifier for each class; one-vs-one trains classifiers for pairs. Some algorithms handle multiclass natively. Class probabilities should sum to one when the model provides a normalised multiclass probability distribution.

A confusion matrix reveals which classes are confused. Accuracy alone can hide poor recall for a rare class. Macro averaging gives each class equal weight; weighted averaging weights by support. Choose the average based on the application and report per-class results.

Class labels may have a natural hierarchy or order. If errors have different severity, a standard multiclass metric may not reflect the cost. Consider ordinal methods or a cost matrix where justified.

## 2. Worked Python example
Run in VS Code with the course virtual environment. Install packages with `python -m pip install numpy pandas matplotlib scikit-learn`. Some dataset loaders may require internet access on first use.

```python
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report

data = load_wine(as_frame=True)
Xtr, Xte, ytr, yte = train_test_split(data.data, data.target,
    test_size=.25, random_state=42, stratify=data.target)
model = RandomForestClassifier(n_estimators=200, random_state=42).fit(Xtr, ytr)
pred = model.predict(Xte)
print(confusion_matrix(yte, pred))
print(classification_report(yte, pred, target_names=data.target_names))
```

## 3. Interpretation and checks
Record the target, sample size, split design, metric and model settings. Inspect class-wise results or residuals, not only the headline score. Keep the test set untouched during model selection and report dataset limitations.

## 4. Guided practice
Identify the class with the lowest recall. Explain why macro F1 and weighted F1 may differ and choose which should be highlighted when class frequencies are unequal.

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
