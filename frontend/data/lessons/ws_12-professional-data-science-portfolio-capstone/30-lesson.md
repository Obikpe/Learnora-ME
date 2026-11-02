# Lesson 30: Capstone: Validation and Iteration

## Learning outcomes

By the end of this lesson, you should be able to Iterate the capstone using validation and error analysis; record changes and reasons; test sensitivity to assumptions; and avoid choosing changes on the final test set.

## 1. Core explanation
Validation checks whether findings are robust to reasonable changes in assumptions, samples or methods. For predictive work, use held-out data and inspect errors. For descriptive analysis, test whether conclusions change when definitions, date ranges or outlier handling vary. For statistical comparisons, examine assumptions and effect sizes.

Iteration should respond to evidence. If a feature is unreliable, remove it or improve its source. If a model overfits, simplify or regularise it. If the sample is biased, limit claims or seek better data. Do not iterate solely to produce a preferred result.

Record each change and why it was made. Keep the original result for comparison. State which conclusions are robust and which depend on assumptions. A defensible project can conclude that the evidence is insufficient.

## 2. Worked example or template
Run the Python example in VS Code where applicable. Adapt paths and fields to your own dataset; do not publish restricted records.

```python
validation_log = [
    {"change": "Exclude incomplete month", "reason": "Denominator unavailable", "effect": "Trend estimate changed"},
    {"change": "Use rate rather than count", "reason": "Population size varies", "effect": "Group ranking changed"}
]
for item in validation_log:
    print(item)
```

## 3. Capstone application
Maintain a decision log and connect every analysis step to the project charter. Preserve provenance and reproducibility. Separate observed results from interpretation and recommendations.

## 4. Guided practice
Run at least two sensitivity checks. Explain whether the main conclusion changes and how that affects the strength of your recommendation.

## 5. Independent practice
Complete the corresponding capstone deliverable. Ask a reviewer to reproduce or challenge one result and record the changes made in response.

## 6. Knowledge check
1. What evidence does this deliverable provide?
2. Which assumptions or limitations affect the conclusion?
3. How can another person reproduce the work?
4. What is the next responsible action?

## Lesson summary
A capstone demonstrates an end-to-end professional process: a well-framed question, defensible data, reproducible analysis, validation, clear communication and responsible publication.