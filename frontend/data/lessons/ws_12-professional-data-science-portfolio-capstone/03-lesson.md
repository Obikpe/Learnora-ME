# Lesson 3: Research Questions and Success Criteria

## Learning outcomes
Explain the professional practice, apply it to a data-science project and produce evidence that another person can review.

## 1. Core explanation
A research question narrows the analysis to something answerable with available data. A descriptive question asks what happened; a comparative question asks how groups differ; an association question asks whether variables move together; a predictive question asks how accurately an outcome can be estimated; a causal question asks what would happen under an intervention.

Success criteria must match the question. For a dashboard, criteria may include data freshness, completeness and decision usefulness. For a predictive model, define a metric, evaluation design and baseline. For an experiment, define the outcome, treatment, comparison and analysis plan before examining results.

Avoid changing the question after seeing a convenient result without disclosing the change. Exploratory analysis can generate hypotheses, but confirmatory analysis should be planned and interpreted with appropriate caution.

## 2. Worked example or template
Use the example as a starting point and adapt it to your own project. Python examples run in VS Code; shell commands should be entered in the VS Code terminal.

```python
research_plan = {
    "question": "Did the new reminder increase on-time assignment submission?",
    "outcome": "Submitted by the published deadline",
    "comparison": "Eligible learners receiving reminder vs comparable group",
    "period": "Four weeks",
    "metric": "Difference in on-time submission rate",
    "caveat": "Non-random assignment may confound the comparison"
}
print(research_plan)
```

## 3. Professional application
Keep claims evidence-based. Document sources, assumptions, licences, decisions and limitations. A portfolio project should be understandable and reproducible without access to private data or undocumented local files.

## 4. Guided practice
Write three research questions for a public transport dataset: one descriptive, one comparative and one predictive. For each, state the required variables and a success criterion.

## 5. Independent practice
Create the corresponding artefact in your project repository. Ask another person to review it and record what was unclear or incomplete.

## 6. Knowledge check
1. What is the purpose of this professional practice?
2. What evidence should be preserved?
3. Which risks or constraints need to be disclosed?
4. How will another person verify the work?

## Lesson summary
Professional data science combines sound analysis with ethical judgement, reproducible practice and clear communication.