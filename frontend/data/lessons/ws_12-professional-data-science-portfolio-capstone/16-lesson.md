# Lesson 16: Writing an Executive Summary

## Learning outcomes
Apply the professional method, produce a project artefact and communicate decisions with evidence.

## 1. Core explanation
An executive summary is a concise decision-oriented account of a longer analysis. It should state the problem, the most important evidence, what it means, the recommended action and the key limitation. Write it for a reader who may not read the technical appendix.

Avoid opening with a long description of tools. The stakeholder usually cares about the decision and impact. Use specific quantities with units and comparison periods. If the result is uncertain, say so. Do not bury a major limitation in the final paragraph.

Recommendations should be proportional to evidence. A descriptive trend may justify further investigation, not a causal intervention. A predictive model with weak subgroup performance may justify a restricted pilot rather than broad deployment.

## 2. Worked example or template
Use the example in VS Code or adapt the structure to your project.

```python
summary = {
    "problem": "On-time assignment submission is declining",
    "evidence": "Rate fell from 82% to 74% over the measured period",
    "interpretation": "Decline is concentrated in two cohorts; cause is not established",
    "recommendation": "Review support access and collect cohort-level feedback",
    "limitation": "Only six weeks of comparable records are available"
}
for key, value in summary.items():
    print(f"{key.title()}: {value}")
```

## 3. Professional application
Keep the artefact reproducible and honest. State the data source, time period, methods, your contribution and limitations. Do not publish confidential data or make unsupported performance claims.

## 4. Guided practice
Write a 150-200 word executive summary for a project. Include a measured finding, a cautious interpretation, a recommendation and a limitation. Remove tool names unless they materially affect the decision.

## 5. Independent practice
Create or improve the corresponding project artefact. Ask another person to review it and record any unclear assumptions or missing instructions.

## 6. Knowledge check
1. What decision or audience does this artefact serve?
2. What evidence supports the claim?
3. Which limitations must be disclosed?
4. How can another person verify the work?

## Lesson summary
A professional portfolio demonstrates judgement, evidence, reproducibility and communication—not just familiarity with tools.