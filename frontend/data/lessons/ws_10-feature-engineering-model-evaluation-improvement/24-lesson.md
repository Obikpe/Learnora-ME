# Lesson 24: Feature Engineering and Model Evaluation Project

## Project purpose
This final project brings together feature engineering, leakage prevention, preprocessing, feature selection, validation, evaluation and model improvement. Your goal is not to produce the highest possible score at any cost. Your goal is to build a defensible workflow and explain what the evidence supports.

## Learning outcomes
By the end of this project, you should be able to frame a predictive task; document prediction-time feature availability; create and compare engineered features; build leakage-safe pipelines; evaluate with an appropriate split and metric; diagnose errors; and communicate a responsible recommendation.

![End-to-end model improvement workflow](/course-assets/ws10/reproducible-workflow.svg)

## 1. Choose a problem
Select a public dataset with a clear licence and a target that supports a meaningful prediction task. Suitable examples include customer churn, loan repayment, product demand, energy use or delivery duration. State:
- what one row represents;
- what outcome is being predicted;
- when the prediction would be made;
- who would use the prediction;
- what action the prediction could support.

If the data does not contain a defensible target, do not invent one simply to fit a classifier. You may choose another dataset or conduct a feature-engineering analysis with an appropriately different objective.

## 2. Data audit
Inspect shape, data types, duplicates, missingness, category counts, target distribution and date coverage. Identify identifiers, possible leakage columns and fields recorded after the prediction time. Write a short data-quality report before modelling.

## 3. Feature dictionary
For every feature record its name, meaning, source, type, unit, calculation, time window, missing-value interpretation and earliest availability. For each engineered feature, justify why it may help and why it is available at prediction time.

## 4. Baseline workflow
Create a simple baseline with an appropriate preprocessing pipeline. Split the data before fitting learned transformations. Use a random stratified split only when observations are independent; use group-aware or chronological splitting when the problem requires it.

Build all preprocessing inside a Pipeline and ColumnTransformer. Fit imputation, encoding, scaling and selection only on training folds.

## 5. Candidate improvements
Test at least three controlled changes, such as:
1. a recency or frequency feature;
2. a categorical encoding or numeric transformation choice;
3. a feature-selection or regularisation approach;
4. a different estimator or hyperparameter setting.

Do not change everything at once. Use the same cross-validation folds and metric for fair comparison. Record each experiment even if it does not improve performance.

## 6. Evaluation and error analysis
Choose metrics based on the problem. For regression, report MAE and RMSE and inspect residuals. For classification, report a confusion matrix, precision, recall and F1; add ROC-AUC or average precision where appropriate. Explain class prevalence and the positive class.

Inspect examples of errors and performance across meaningful groups. If selecting a classification threshold, use validation predictions and justify the cost or capacity assumptions. Keep the final test set untouched until the workflow is selected.

## 7. Suggested repository
```text
feature-evaluation-project/
├── README.md
├── requirements.txt
├── data/README.md
├── notebooks/exploration.ipynb
├── src/
│   ├── features.py
│   ├── preprocessing.py
│   ├── pipeline.py
│   └── evaluate.py
└── reports/
    ├── feature_dictionary.csv
    ├── experiment_log.csv
    └── final_evaluation.md
```

Do not publish private records, credentials or restricted data. Provide lawful data acquisition instructions instead of committing sensitive files.

## 8. Final report structure
1. Problem and intended decision.
2. Dataset source, licence and observation grain.
3. Data-quality findings.
4. Target definition and prediction time.
5. Feature dictionary and engineering rationale.
6. Leakage risks and safeguards.
7. Split and validation strategy.
8. Baseline results.
9. Candidate experiments and comparison table.
10. Final test result and error analysis.
11. Limitations, fairness considerations and monitoring plan.
12. Recommendation: adopt, reject or gather more evidence.

## 9. Assessment rubric
| Criterion | Weight |
|---|---:|
| Problem framing and prediction-time definition | 10% |
| Data audit and feature dictionary | 15% |
| Leakage prevention and pipeline design | 20% |
| Feature engineering rationale and implementation | 15% |
| Validation, metrics and model comparison | 20% |
| Error analysis, limitations and communication | 20% |

## 10. Final reflection
Answer these questions in your own words:
- Which feature change produced the most useful improvement?
- Was the improvement consistent across folds?
- Which feature did you reject and why?
- What leakage risk was hardest to detect?
- What does the final test result not prove?
- What would you monitor if the model were used in production?

## Completion standard
A successful project is not defined by a perfect score. It is defined by a clear prediction task, valid feature timing, reproducible transformations, honest evaluation and a thoughtful explanation of uncertainty. A model that performs slightly less well but is robust, interpretable and operationally feasible may be the better choice.