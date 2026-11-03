# Lesson 2: Regression and Classification Targets

## Learning outcomes

By the end of this lesson, you should be able to Distinguish regression targets from binary and multiclass classification targets; identify target data types; and explain how the target definition determines the modelling task and evaluation metrics.

## 1. Core explanation
A regression target is a numeric quantity where distances between values matter, such as price or delivery duration. A classification target is a category, such as approved/declined or fraud/not fraud. Binary classification has two classes; multiclass classification has more than two. Multi-label classification allows more than one label per observation.

The target's meaning determines the task. A numeric code for categories does not make a regression problem. If product type is encoded 0, 1 and 2, predicting 1.4 is meaningless. Conversely, a numeric measurement such as temperature should not usually be converted into arbitrary categories because doing so loses information.

Target construction needs care. Check class definitions, inconsistent labels, rare classes and delayed outcomes. For regression, inspect range, skew and impossible values. For classification, inspect class proportions and whether classes are mutually exclusive. Document how ambiguous cases are handled.

## 2. Worked example
Use VS Code and a project virtual environment. Install the packages used in this lesson with `python -m pip install numpy pandas matplotlib scikit-learn`.

```python
import pandas as pd

df = pd.DataFrame({
    "house_price": [120000, 185000, 210000],
    "loan_status": ["paid", "late", "paid"],
    "product_type": ["phone", "laptop", "phone"]
})
print(df.dtypes)
print(df["loan_status"].value_counts())
print(df["product_type"].value_counts())
```

## 3. Interpretation and diagnostics
Explain what each feature and target represent, the units of the output and how the model was evaluated. Inspect errors and check that all preprocessing was learned from training data only. Never infer causation from predictive coefficients without a suitable causal design.

## 4. Guided practice
For a dataset containing age, income, customer segment and churn status, identify which column is the target for a churn classifier. Explain why customer segment encoded as 1, 2 and 3 is not a valid numeric regression target.

## 5. Independent practice
Apply the method to a dataset of your choice. Define the prediction moment, target and feature availability. Compare with a simple baseline and report at least one metric plus an error analysis.

## 6. Knowledge check
1. What does the model estimate?
2. What assumptions or limitations matter most?
3. How could leakage or an inappropriate split inflate performance?
4. What additional analysis is needed before use?

## Lesson summary
Supervised models must be framed around a precise target and evaluated on unseen data. Model complexity and scores matter less than reliable performance for the intended decision.

## 7. Learn the idea, not just the API

When studying this technique, separate three questions that are often mixed together:

1. **What is the model trying to learn?** Identify the input information, the outcome and the mathematical quantity the algorithm adjusts. Be able to explain this without mentioning a Python library.
2. **What does the fitted result mean?** Translate a prediction, coefficient, probability, split, metric or parameter into the units and context of the problem. A numerical output has no useful interpretation until you know what it represents.
3. **What evidence would make you trust it?** Consider whether the training examples represent the cases where the model will be used, whether the prediction moment is respected, and whether evaluation data remained separate from model fitting.

A useful mental model is that training is practice with known answers, validation is a rehearsal used to choose between approaches, and testing is the final examination. Repeatedly changing a model after looking at test results turns the test set into another validation set. The final score then becomes optimistic because decisions have been indirectly fitted to those examples.

## 8. A careful way to read the Python workflow

Read code from the data outward rather than memorising commands. First identify which columns are inputs and which column is the target. Then find the split operation and ask which observations are held back. Find the fit call: this is where the model learns from the training examples. Find predict or predict_proba: these apply the fitted model to new rows. Finally, locate the metric and verify that it compares predictions with the correct held-out target values.

Parameters are instructions that change behaviour. A parameter such as a maximum depth, regularisation strength, neighbour count or number of estimators is not a magic setting. Ask what happens when it is increased, what trade-off it controls, and how it should be selected. Choose such settings using training/validation data or cross-validation, never by repeatedly optimising the final test score.

## 9. Worked reasoning example

Imagine a platform predicts whether a learner will complete a course. One row represents one learner at the end of week two. The target is completion by the end of week eight. Candidate inputs include attendance up to week two, assignments submitted up to week two and time spent on lessons up to week two.

Before fitting anything, check that no feature contains week-three-to-week-eight information. Split the data so that learners in the evaluation set are not used to fit transformations or model parameters. Compare the candidate with a simple baseline. If the model improves the headline score, inspect which learners it gets wrong and whether those errors are concentrated in a particular group. Then decide whether the improvement is large and reliable enough to support the proposed intervention.

This example illustrates a general rule: a good model is not simply one that scores well. It must answer the intended question at the intended time, using legitimate information, and its errors must be acceptable for the decision.

## 10. Self-study checkpoint

Without looking back at the code, write a short explanation of the technique in your own words. Include its purpose, the kind of data it needs, the central idea behind how it works, one important parameter, one way it can fail and one fair way to evaluate it. Then return to the lesson and correct any gaps. This retrieval exercise is more useful than copying definitions.

## 11. Extended independent exercise

Use a small, documented dataset and produce a reproducible notebook. Your notebook should contain:
- a problem statement and a precise definition of one row;
- a description of the target, features, units and prediction time;
- a check for missing values, duplicates, unusual values and possible leakage;
- a defensible train/validation/test strategy;
- a baseline and the technique from this lesson;
- an evaluation result explained in plain language;
- an error inspection and a discussion of limitations.

Do not remove unusual observations merely because they make the score worse. Investigate whether they are data errors, rare but valid cases or evidence that the model is weak in an important part of the population. Record the reason for every cleaning and modelling decision.

## 12. Knowledge check: explain your reasoning

1. Explain the technique to a learner who has never studied machine learning.
2. What does the model learn from the training examples, and what does it output for a new observation?
3. Which parameter or modelling choice most changes its behaviour? Explain the trade-off.
4. Give an example of leakage or an unfair evaluation design that could produce an overly optimistic result.
5. What additional evidence would you want before using the model to support a real decision?

A strong answer explains why, not only what. If you cannot justify a choice in ordinary language, revisit the relevant section before moving on.
