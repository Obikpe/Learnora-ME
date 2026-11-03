# Lesson 28: Supervised Learning Assessment

## Purpose
This assessment brings together the supervised-learning skills from WS08. You will frame a prediction problem, prepare a dataset, compare appropriate models, evaluate errors and communicate a defensible recommendation. The goal is not to achieve the highest possible score by trying many models. The goal is to demonstrate a reliable process and explain what the evidence supports.

## Learning outcomes

By the end of this lesson, you should be able to Demonstrate the full supervised-learning workflow in an assessed project; frame a defensible target; prevent leakage; compare models; evaluate errors; and submit reproducible code, a report and limitations.


![Supervised learning project workflow](/course-assets/ws08/workflow.svg)

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
