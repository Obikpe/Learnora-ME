# Lesson 24: Feature Engineering and Model Evaluation Project

## Purpose
This final project tests whether you can improve a predictive workflow without leaking information or overfitting the validation process. You will start with a baseline, design features that would genuinely be available at prediction time, compare leakage-safe pipelines and justify whether the improvement is useful.

## Learning outcomes
- define the prediction unit, target, prediction timestamp and decision;
- create a feature data dictionary including source and availability time;
- identify and prevent target leakage, temporal leakage and preprocessing leakage;
- build a ColumnTransformer and model inside a scikit-learn Pipeline;
- compare a baseline and at least two feature/model configurations with suitable cross-validation;
- choose metrics and thresholds based on error costs;
- inspect errors, uncertainty and subgroup performance;
- document a reproducible experiment and a defensible recommendation.

## Project brief
Choose a classification or regression problem with a documented data source and licence. Your dataset must have a clear target and enough observations to support a train/validation design. State the decision that the prediction would support. A descriptive feature-engineering investigation is acceptable only if you explain why a predictive target is unavailable and adjust the evaluation plan.

## Required work
1. Write a problem statement with the target, unit, prediction time and intended action.
2. Audit the raw data: shape, types, missingness, duplicates, target distribution, suspicious IDs and date coverage.
3. Create a feature dictionary with each feature's meaning, source, type, missingness and earliest availability time.
4. Propose candidate engineered features. For every feature, explain why it could help and prove it would be known at prediction time.
5. Split the data before fitting any imputer, encoder, scaler or selector. Use group-aware or time-aware splitting if the data structure requires it.
6. Build a baseline pipeline and at least two candidate pipelines. Keep all learned preprocessing inside the pipeline.
7. Compare candidates on identical cross-validation folds. Record metrics for each fold, not only the mean.
8. Tune only on training data. Keep the final test set untouched until the design is selected.
9. Evaluate the final model once on the test set. Inspect representative errors and relevant subgroup results.
10. Write a decision note: retain the change, reject it or conclude that evidence is insufficient.

## Suggested repository
```text
feature-evaluation-project/
├── README.md
├── requirements.txt
├── data/README.md
├── notebooks/exploration.ipynb
├── src/
│   ├── features.py
│   ├── pipeline.py
│   └── evaluate.py
└── reports/
    ├── feature_dictionary.csv
    ├── experiment_log.csv
    └── evaluation.md
```

Do not publish private data or credentials. The repository should explain how to obtain or reproduce the dataset without committing restricted records.

## Assessment rubric
| Criterion | Weight |
|---|---:|
| Problem framing and prediction-time definition | 15% |
| Data audit and feature dictionary | 15% |
| Leakage prevention and pipeline design | 20% |
| Feature rationale and implementation | 15% |
| Validation, metrics and model comparison | 20% |
| Error analysis, limitations and communication | 15% |

## Final reflection
Explain which feature change made the greatest difference, whether the improvement was stable across folds, what might still cause leakage or distribution shift, and what evidence would be required before deployment.