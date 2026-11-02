# Lesson 29: Capstone: Analysis and Modelling

## Learning outcomes
Apply the professional practice, produce the capstone artefact and communicate evidence and limitations clearly.

## 1. Core explanation
Complete the analysis that answers the approved capstone question. Start with descriptive summaries and visualisations. Check distributions, missingness, relationships and subgroup differences. If prediction is justified, define the target and prediction timestamp, establish a baseline and use a split that reflects intended future use.

Choose methods based on the question and assumptions. For a descriptive project, careful visual analysis and statistical summaries may be sufficient. For a predictive project, use leakage-safe preprocessing and metrics tied to the decision. Record experiments and avoid repeated test-set tuning.

Interpret results in context. Association is not causation, and model performance does not prove that a feature causes the outcome. Consider alternative explanations, measurement limitations and population coverage.

## 2. Worked example or template
Run the Python example in VS Code where applicable. Adapt paths and fields to your own dataset; do not publish restricted records.

```python
# Analysis checklist
# [ ] Descriptive statistics and distributions
# [ ] Relevant subgroup comparisons
# [ ] Visual checks for patterns and anomalies
# [ ] Baseline method or model
# [ ] Validation design justified
# [ ] Metrics match the decision
# [ ] Error or sensitivity analysis
# [ ] Findings mapped to the research question
```

## 3. Capstone application
Maintain a decision log and connect every analysis step to the project charter. Preserve provenance and reproducibility. Separate observed results from interpretation and recommendations.

## 4. Guided practice
Complete the main analysis. Submit notebooks or scripts, an experiment log and a findings memo that separates observations from explanations.

## 5. Independent practice
Complete the corresponding capstone deliverable. Ask a reviewer to reproduce or challenge one result and record the changes made in response.

## 6. Knowledge check
1. What evidence does this deliverable provide?
2. Which assumptions or limitations affect the conclusion?
3. How can another person reproduce the work?
4. What is the next responsible action?

## Lesson summary
A capstone demonstrates an end-to-end professional process: a well-framed question, defensible data, reproducible analysis, validation, clear communication and responsible publication.