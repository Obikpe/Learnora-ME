# Lesson 28: Supervised Learning Assessment

## Purpose
This assessment brings together the supervised-learning skills from WS08. You will frame a prediction problem, prepare a dataset, compare appropriate models, evaluate errors and communicate a defensible recommendation. The goal is not to achieve the highest possible score by trying many models. The goal is to demonstrate a reliable process and explain what the evidence supports.

## Learning outcomes
By the end of this assessment, you should be able to:
- distinguish a regression target from a classification target and define the prediction unit and time;
- create a reproducible train/test split appropriate to the data;
- build a leakage-safe preprocessing and modelling pipeline;
- establish a simple baseline and compare it with at least two suitable supervised models;
- select metrics based on the decision and error costs;
- interpret model errors, limitations and uncertainty;
- present reproducible code and a clear recommendation.

## Assessment brief
Choose one of the following routes, or propose a comparable dataset with a documented source and licence.

### Route A: Regression
Use the California housing dataset or another approved numeric-target dataset. Predict a continuous outcome. Compare a DummyRegressor baseline with at least two models. Report MAE and RMSE, inspect residuals and explain what a typical error means in the target's units.

### Route B: Classification
Use the Wine or Breast Cancer dataset, or another approved labelled dataset. Predict a class. Compare a DummyClassifier baseline with at least two models. Report a confusion matrix and at least two suitable metrics. If probabilities are used, discuss calibration and threshold choice.

## Required workflow
1. **Frame the task.** State the stakeholder decision, prediction unit, target definition, prediction time, population and intended action. Explain why the target is available and meaningful.
2. **Audit the data.** Record rows, columns, types, missingness, duplicates, class balance or target range, and any suspicious identifiers. Create a short data dictionary.
3. **Split before learning from data.** Hold out a final test set. Use stratification for classification when appropriate. For time-dependent or grouped observations, explain why a random split may be invalid and choose a time- or group-aware split.
4. **Build a baseline.** A baseline establishes the performance that a simple rule can achieve. Do not treat a high accuracy score as meaningful without comparing it to a suitable baseline.
5. **Build model pipelines.** Put imputers, encoders, scalers and feature selection inside the pipeline so they are fitted only on training folds. Use cross-validation on the training data for model comparison and tuning.
6. **Evaluate once on the final test set.** Do not select models, features or thresholds using the test set. Report the metric, test population and uncertainty or limitations.
7. **Analyse errors.** Inspect representative errors, identify patterns and discuss the consequences of false positives, false negatives or large residuals.
8. **Communicate.** Write a short report that separates observed results, interpretation and recommendation. State limitations and what further evidence is required.

## Submission structure
```text
supervised-assessment/
├── README.md
├── data/README.md
├── notebooks/analysis.ipynb
├── src/
│   ├── prepare.py
│   └── train.py
├── reports/
│   ├── evaluation.md
│   └── figures/
└── requirements.txt
```

Do not commit private, licensed or restricted data unless redistribution is explicitly permitted. Include data download instructions or a safe sample instead.

## Marking rubric
| Criterion | Weight |
|---|---:|
| Problem framing and target definition | 10% |
| Data audit and preparation | 15% |
| Leakage prevention and reproducibility | 20% |
| Baseline and model comparison | 15% |
| Metrics and validation design | 20% |
| Error analysis and interpretation | 10% |
| Communication, ethics and limitations | 10% |

## Self-review checklist
- Can another learner reproduce the result from the README?
- Is the target defined without ambiguity or future-information leakage?
- Were transformations fitted only on training data?
- Does the metric match the real decision?
- Is the final test set kept separate from model selection?
- Are errors and limitations explained honestly?
- Does the recommendation follow from the evidence?

## Reflection
In 300–500 words, explain the most consequential modelling decision you made, one approach you rejected and why, what the evaluation does not prove, and what you would do before using the model in a real organisation.