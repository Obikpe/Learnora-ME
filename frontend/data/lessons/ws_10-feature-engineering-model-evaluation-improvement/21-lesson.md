# Lesson 21: Model Comparison and Statistical Caution

## Learning outcomes
Explain the technique, implement it in Python and justify the validation choices.

## 1. Core explanation
Model scores vary with sample, split and random seed. A small difference in mean cross-validation score may not be meaningful. Report fold-level variability, sample size and uncertainty. If comparing models on the same folds, their scores are paired; inspect the distribution of differences rather than comparing rounded means alone.

Repeatedly selecting the best among many candidates can produce optimistic estimates. Nested cross-validation can estimate the full selection process, while a final held-out test provides a final check. Neither removes sampling bias or future distribution shift.

Statistical significance is not the same as practical value. Consider effect size, operational cost, fairness, interpretability and latency. If two models perform similarly, prefer the simpler and more maintainable one unless a clear benefit justifies complexity.

## 2. Worked Python example
Run in VS Code using the course virtual environment. Install packages with `python -m pip install numpy pandas scipy matplotlib scikit-learn`.

```python
import numpy as np
scores_a = np.array([.91, .90, .93, .89, .92])
scores_b = np.array([.92, .91, .92, .90, .93])
differences = scores_b - scores_a
print("Mean A:", scores_a.mean(), "Mean B:", scores_b.mean())
print("Fold differences:", differences)
print("Mean paired difference:", differences.mean())
```

## 3. Interpretation and safeguards
State the metric, split design and assumptions. Keep preprocessing and feature selection inside the training workflow. Do not use the final test set to tune thresholds, select features or choose hyperparameters.

## 4. Guided practice
Interpret the paired fold differences. Explain why five folds do not prove a universal performance advantage and why practical cost should influence the choice.

## 5. Independent practice
Apply the method to a dataset you understand. Record a baseline, define a hypothesis before each change and keep an experiment log. Explain whether any improvement is stable and practically important.

## 6. Knowledge check
1. What question does this method answer?
2. What data leakage risk must be controlled?
3. How does the metric relate to the decision?
4. What evidence would make you trust the improvement?

## Lesson summary
Reliable model improvement requires controlled experiments, leakage-safe preprocessing, a validation design that matches the data and honest reporting of uncertainty.