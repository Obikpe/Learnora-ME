# Lesson 24: Communicating Uncertainty and Limitations

## Learning outcomes
Apply the professional practice, produce the capstone artefact and communicate evidence and limitations clearly.

## 1. Core explanation
Every analysis has uncertainty: sampling variation, measurement error, missing data, model assumptions, changing populations and incomplete coverage. Communicate what is known, how strong the evidence is and what remains unknown. Avoid false precision and absolute claims.

Use confidence intervals or ranges where appropriate. For predictive models, explain the evaluation population and error profile. For descriptive reports, state the time window and denominator. For causal claims, describe the design and plausible confounders. A chart or p-value does not remove these limitations.

Limitations should influence recommendations. If evidence is weak, propose further data collection or a limited pilot. If a model fails for a subgroup, restrict use until the issue is addressed. Honest caveats improve trust and prevent inappropriate decisions.

## 2. Worked example or template
Run the Python example in VS Code where applicable. Adapt paths and fields to your own dataset; do not publish restricted records.

```python
uncertainty_note = {
    "estimate": "74% on-time completion",
    "period": "Six-week observation window",
    "uncertainty": "Small cohort counts; interval estimates are wide",
    "limitation": "No comparison group, so causes are unknown",
    "next_step": "Collect a longer period and compare cohorts"
}
for k, v in uncertainty_note.items():
    print(k.title(), v)
```

## 3. Capstone application
Maintain a decision log and connect every analysis step to the project charter. Preserve provenance and reproducibility. Separate observed results from interpretation and recommendations.

## 4. Guided practice
Write a limitations paragraph for a project with a small, non-random sample. Include sampling, measurement and generalisation limitations, plus the next evidence needed.

## 5. Independent practice
Complete the corresponding capstone deliverable. Ask a reviewer to reproduce or challenge one result and record the changes made in response.

## 6. Knowledge check
1. What evidence does this deliverable provide?
2. Which assumptions or limitations affect the conclusion?
3. How can another person reproduce the work?
4. What is the next responsible action?

## Lesson summary
A capstone demonstrates an end-to-end professional process: a well-framed question, defensible data, reproducible analysis, validation, clear communication and responsible publication.