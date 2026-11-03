# Lesson 10: Classification Thresholds and Probabilities

## Learning outcomes

By the end of this lesson, you should be able to Convert predicted probabilities into class labels at different thresholds; calculate precision and recall; explain the trade-off; and choose a threshold using the costs and capacity of the intended decision.

## 1. Core explanation
A classifier may output a probability for each class. The threshold converts a probability into a class label. With a threshold of 0.5, a positive class is predicted when its estimated probability is at least 0.5. Lowering the threshold usually increases recall and may reduce precision; raising it usually increases precision and may reduce recall.

The threshold should reflect the decision. In screening, missing a true positive may be costly, so higher recall may be preferred even if more false alarms occur. In an expensive intervention programme, false positives may consume scarce resources, so precision may matter more. The threshold must be selected using validation data, not repeatedly adjusted against the final test set.

A predicted probability is not automatically trustworthy. Calibration asks whether cases assigned probability 0.8 are positive about 80% of the time. Evaluate calibration separately from ranking metrics. Explain that a score is an estimate, not certainty.

## 2. Worked Python example
Run in VS Code using the course virtual environment. Install required packages with `python -m pip install numpy pandas matplotlib scikit-learn`. Some dataset loaders may need internet access on first use.

```python
import numpy as np
from sklearn.metrics import precision_score, recall_score

y_true = np.array([0, 0, 1, 1, 1, 0, 1, 0])
prob = np.array([.1, .4, .45, .55, .8, .2, .7, .6])
for threshold in [.3, .5, .7]:
    pred = (prob >= threshold).astype(int)
    print(threshold, "precision", precision_score(y_true, pred),
          "recall", recall_score(y_true, pred))
```

## 3. Interpretation and checks
Record the target, sample size, split design, metric and model settings. Inspect class-wise results or residuals, not only the headline score. Keep the test set untouched during model selection and report the limitations of the dataset.

## 4. Guided practice
Use the values to compare thresholds 0.3, 0.5 and 0.7. State which threshold you would choose if false negatives cost four times as much as false positives, and explain what other information you need.

## 5. Independent practice
Extend the example with a second model or a different evaluation view. Keep a record of every change and compare candidates using the same training/validation design. Write a short report for a non-technical stakeholder.

## 6. Knowledge check
1. What does this method optimise or estimate?
2. Which assumptions or settings affect its behaviour?
3. How would you detect overfitting or leakage?
4. What evidence is needed before the model is used?

## Lesson summary
Supervised learning is a complete evidence-based process: define the target, preserve the prediction timeline, validate fairly, inspect errors and communicate uncertainty.

## 7. Learn the idea, not just the API

Separate three questions when studying this method. First, what is it trying to learn from the examples? Identify its inputs, target and the quantity or structure adjusted during training. Second, what does its fitted output mean in the real problem? Translate predictions, coefficients, probabilities, splits and metrics into the original units. Third, what evidence would make the result trustworthy? Check whether the data represents future use, whether the prediction timeline is respected and whether evaluation observations were kept separate from fitting.

Training is practice with known answers. Validation is a rehearsal used to choose between approaches. Testing is the final examination. Repeatedly changing a model after inspecting test results turns the test set into another validation set and makes the final score optimistic.

## 8. Read the implementation carefully

Read the Python workflow from the data outward. Identify the input columns and target. Find the split operation and establish which rows are held back. Find fit: this is where the model learns. Find predict or predict_proba: these apply the fitted model to new rows. Finally, locate the metric and confirm that it compares predictions with the correct held-out target values.

A parameter is an instruction that changes behaviour, not a magic setting. Ask what happens when it increases, what trade-off it controls and how it should be selected. Use training/validation data or cross-validation to choose settings, never repeated optimisation of the final test score.

## 9. Worked reasoning example

Imagine a learning platform predicts whether a learner will complete a course. One row represents a learner at the end of week two; the target is completion by the end of week eight. Candidate inputs include attendance, assignments submitted and lesson activity recorded up to week two. Before fitting, check that no feature contains week-three-to-week-eight information. Compare the model with a simple baseline. If the model improves the headline score, inspect which learners it gets wrong and whether errors are concentrated in a particular group. Decide whether the improvement is reliable and useful enough to support the proposed intervention.

A good model is not simply one that scores well. It must answer the intended question at the intended time, use legitimate information and make errors that are acceptable for the decision.

## 10. Self-study and independent exercise

Without looking at the code, explain the method in your own words. Include its purpose, required data, central idea, one important parameter, one failure mode and one fair evaluation method. Then use a documented dataset to create a reproducible notebook containing a precise problem statement, target and feature definitions, data-quality checks, a defensible split, a baseline, the method from this lesson, an explained evaluation result and an error analysis.

Do not remove unusual observations merely because they worsen the score. Investigate whether they are data errors, rare but valid cases or evidence of weak model performance. Record the reason for every cleaning and modelling decision.

## 11. Knowledge check: explain your reasoning

1. Explain the method to someone new to machine learning.
2. What does it learn from training examples, and what does it return for a new observation?
3. Which setting most changes its behaviour? Explain the trade-off.
4. Give an example of leakage or unfair evaluation that could inflate performance.
5. What further evidence is needed before using the model in a real decision?

A strong answer explains why, not only what. Revisit the relevant section if you cannot justify a choice in ordinary language.
