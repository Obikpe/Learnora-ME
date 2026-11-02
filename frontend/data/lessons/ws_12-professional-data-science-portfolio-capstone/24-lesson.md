# Lesson 24: Communicating Uncertainty and Limitations

## Learning outcomes

By the end of this lesson, you should be able to Communicate uncertainty from sampling, measurement, missingness and modelling; state the population and time window; and make recommendations proportionate to evidence strength.

## 1. Core explanation
Every analysis has uncertainty: sampling variation, measurement error, missing data, model assumptions, changing populations and incomplete coverage. Communicate what is known, how strong the evidence is and what remains unknown. Avoid false precision and absolute claims.

Use confidence intervals or ranges where appropriate. For predictive models, explain the evaluation population and error profile. For descriptive reports, state the time window and denominator. For causal claims, describe the design and plausible confounders. A chart or p-value does not remove these limitations.

Limitations should influence recommendations. If evidence is weak, propose further data collection or a limited pilot. If a model fails for a subgroup, restrict use until the issue is addressed. Honest caveats improve trust and prevent inappropriate decisions.

## 2. Worked example or template
Use the example as a starting point and adapt it to your own project. Python examples run in VS Code; shell commands should be entered in the VS Code terminal.

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

## 3. Professional application
Keep claims evidence-based. Document sources, assumptions, licences, decisions and limitations. A portfolio project should be understandable and reproducible without access to private data or undocumented local files.

## 4. Guided practice
Write a limitations paragraph for a project with a small, non-random sample. Include sampling, measurement and generalisation limitations, plus the next evidence needed.

## 5. Independent practice
Create or improve the corresponding project artefact in your repository. Ask another person to review it and record what was unclear or incomplete.

## 6. Knowledge check
1. What is the purpose of this professional practice?
2. What evidence should be preserved?
3. Which risks or constraints need to be disclosed?
4. How will another person verify the work?

## Lesson summary
Professional data science combines sound analysis with ethical judgement, reproducible practice and clear communication.