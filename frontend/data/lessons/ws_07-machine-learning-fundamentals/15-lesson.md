# Lesson 15: Ethics, Bias and Responsible ML

## Learning outcomes
Explain the method, implement the example in Python, interpret its result, and identify risks that could invalidate the conclusion.

## 1. Concepts and reasoning
A model learns from data shaped by human decisions, institutions and historical conditions. If a training dataset under-represents a group or reflects unequal past treatment, model performance may differ across groups. A single overall accuracy score can hide those differences.

Fairness is not one metric. Different definitions can conflict, especially when base rates differ. Start by identifying affected groups, the decision being automated or supported, potential harms, legal and organisational obligations, and who can appeal an outcome. Measure error rates and calibration across relevant groups where lawful and appropriate, while protecting privacy.

Responsible ML also requires data minimisation, access control, security, documentation, explainability proportionate to risk and human oversight. Do not collect sensitive attributes casually. However, excluding a protected attribute does not guarantee fairness because proxy variables may encode similar information. A model should not be deployed merely because it achieves a high aggregate score.

## 2. Worked example
Run in VS Code in your course virtual environment. Install packages as required: `python -m pip install numpy pandas scikit-learn matplotlib`.

```python
import pandas as pd
from sklearn.metrics import accuracy_score

results = pd.DataFrame({
    "group": ["A", "A", "A", "A", "B", "B", "B", "B"],
    "actual": [1, 1, 0, 0, 1, 1, 0, 0],
    "predicted": [1, 1, 0, 0, 1, 0, 0, 0]
})
print(results.groupby("group").apply(
    lambda g: accuracy_score(g["actual"], g["predicted"]),
    include_groups=False
))
```

## 3. Interpretation
State what was learned from training data and what was measured on unseen data. Check whether the metric answers the real decision question. A technically correct output can still be misleading if the target, split or population is wrong.

## 4. Guided practice
Design a pre-deployment review for a model that prioritises job applicants. Identify affected stakeholders, possible harms, group-level error measures, privacy safeguards, human review and an appeal process. Explain why one fairness metric cannot settle every ethical question.

## 5. Independent practice
Apply the lesson to a small dataset. Record the source, unit of observation, target and feature availability. Save your code and a short report that includes evidence, limitations and the next validation step.

## 6. Knowledge check
1. What assumption is most important in this method?
2. What is the difference between training performance and generalisation?
3. How could leakage or sampling bias affect the result?
4. What would you tell a stakeholder before they use the model?

## Lesson summary
A trustworthy ML workflow is reproducible, uses a suitable baseline and evaluation design, and communicates errors and limitations as carefully as headline performance.