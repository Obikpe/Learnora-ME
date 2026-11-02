# Feature Engineering, Model Evaluation & Improvement
Course: ws_10
Level: Intermediate to advanced
Duration: 18h • 24 lessons
Prerequisite: WS01–WS09; Python, statistics, Pandas, supervised and unsupervised learning

## Course purpose
Improve the quality and reliability of machine-learning systems through thoughtful feature design, leakage-safe preprocessing, rigorous evaluation, error analysis and controlled optimisation. This course deepens model practice rather than simply adding algorithms.

## Learning outcomes
Design useful features; encode and transform variables; handle missingness and outliers; build preprocessing pipelines; use cross-validation correctly; select metrics; tune models efficiently; interpret errors; assess calibration and subgroup performance; and document reproducible improvements.

## Lesson sequence
01. Why Features Matter — representation, signal, domain knowledge and the limits of feature engineering.
02. Feature Engineering Workflow — define hypothesis, inspect raw variables, create candidates and validate usefulness.
03. Numeric Transformations — scaling, log/power transforms, bins, ratios and zero/negative-value cautions.
04. Categorical Feature Engineering — one-hot, ordinal, frequency and rare-category handling.
05. Date and Time Features — calendar parts, elapsed time, cyclical encodings and temporal leakage.
06. Text-Derived Features — token counts, TF-IDF overview, text length and privacy concerns.
07. Interaction and Polynomial Features — interactions, nonlinearities, complexity and regularisation.
08. Domain-Based Features — rates, aggregates, behavioural windows and point-in-time correctness.
09. Missing-Value Strategies — imputation, missingness indicators and missing-not-at-random caveats.
10. Outlier Treatment and Robust Methods — investigation, clipping, robust scaling and preserving valid extremes.
11. Feature Selection — filter, wrapper and embedded methods; stability and leakage risks.
12. Leakage-Safe Preprocessing Pipelines — ColumnTransformer, Pipeline, fit/transform boundaries and reproducibility.
13. Evaluation Design and Data Splitting — random, stratified, grouped and time-based validation.
14. Cross-Validation in Practice — fold design, variance, repeated CV and computational trade-offs.
15. Choosing Metrics for the Decision — regression/classification metrics, asymmetric costs and business thresholds.
16. Calibration and Probability Quality — calibration curves, Brier score concepts and probability interpretation.
17. Error Analysis — residual slices, confusion matrix slices, subgroup and segment-level diagnostics.
18. Threshold and Cost Optimisation — decision thresholds, expected cost and operational constraints.
19. Hyperparameter Search Strategies — grid, random, successive halving concepts and search-space design.
20. Feature Importance and Explainability — permutation importance, coefficients, tree importance and correlated-feature caveats.
21. Robustness, Sensitivity and Stability — perturbation, drift, resampling and stability across folds.
22. Fairness and Subgroup Evaluation — group metrics, trade-offs, small samples and responsible interpretation.
23. Controlled Model Improvement Experiment — baseline, one change at a time, experiment log and reproducible comparison.
24. Model Improvement Capstone — defend feature choices, validation design, metrics, errors and final recommendation.

## Tools
Python, Pandas, NumPy, scikit-learn, Matplotlib and Seaborn. Use pipelines and explicit split boundaries. Avoid unnecessary expensive searches.

## Assessment
Feature design exercises, leakage audits, metric selection, error-analysis reports and a capstone demonstrating measured improvement over a baseline.

## Completion standard
Learners can improve models systematically and explain whether an apparent gain is valid, stable, meaningful and safe to use.
