# Lesson 22: Model Comparison and Statistical Caution

## Learning outcomes
Compare models using identical validation folds; interpret mean and variation; understand uncertainty in metric estimates; recognise practical versus statistical significance; and communicate limitations responsibly.

## 1. Fair comparison requires the same conditions
Two models should be compared on the same observations, target definition, preprocessing rules, folds and metric. If one model is evaluated on easier folds, its score is not directly comparable. Use the same cross-validation splitter and random seed where appropriate.

Record more than the mean score. Include fold-level results, standard deviation, fit time, prediction time, model size and operational constraints. A tiny performance gain may not justify a much more expensive or less interpretable model.

## 2. Why metrics are uncertain
A test score is calculated from a finite sample. If another representative sample were collected, the score would likely differ. Rare positive cases can make precision and recall especially unstable. A difference of 0.002 between models may be noise rather than a meaningful improvement.

Fold scores are related because training sets overlap. Their standard deviation is useful as a descriptive stability measure, but should not be treated as a formal confidence interval without appropriate assumptions.

## 3. Paired comparisons
When models are evaluated on the same folds, compare their fold-level differences. A paired design reduces some variation because both models face similar validation samples. Statistical tests may be appropriate in some settings, but their assumptions must be checked. Statistical significance does not automatically imply practical value.

![Model comparison process](/course-assets/ws10/model-comparison.svg)

## 4. Worked comparison
```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import numpy as np

X, y = load_breast_cancer(return_X_y=True)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

models = {
    "logistic": make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=3000)
    ),
    "random_forest": RandomForestClassifier(
        n_estimators=300, random_state=42
    )
}

scores = {}
for name, model in models.items():
    fold_scores = cross_val_score(
        model, X, y, cv=cv, scoring="roc_auc"
    )
    scores[name] = fold_scores
    print(name, np.round(fold_scores, 3),
          "mean", round(fold_scores.mean(), 3),
          "std", round(fold_scores.std(), 3))

print("Paired fold differences:",
      np.round(scores["random_forest"] - scores["logistic"], 3))
```

This comparison uses the same folds and metric. Five folds are still only a limited view. The paired differences help show whether one model consistently leads across these partitions, but do not prove that it will always be better.

## 5. Practical model selection
Choose a model based on the full decision context: performance, stability, calibration, fairness, interpretability, latency, maintenance and cost. A slightly lower-scoring model may be preferable if it is simpler, more reliable and easier to monitor.

## 6. Common mistakes
- Comparing models on different test samples.
- Reporting only the best fold.
- Treating fold standard deviation as a formal confidence interval.
- Declaring a winner based on a tiny score difference.
- Ignoring compute and maintenance cost.
- Confusing statistical significance with business significance.

## Guided practice
Model A has mean F1 0.91 with standard deviation 0.02; Model B has mean F1 0.915 with standard deviation 0.05. Explain why the evidence may not justify choosing B.

## Independent practice
Compare three models on identical folds. Report per-fold scores, mean, standard deviation, fit time and a practical recommendation. Include uncertainty and limitations in the report.

## Knowledge check
1. Why must models use identical folds?
2. What does fold variation tell you?
3. Why are fold scores not independent samples?
4. What is practical significance?
5. Name two non-metric factors in model choice.

## Lesson summary
Model comparison is an evidence-based decision, not a contest to find the largest decimal. Keep conditions identical, describe uncertainty and choose a model that is useful and maintainable in practice.