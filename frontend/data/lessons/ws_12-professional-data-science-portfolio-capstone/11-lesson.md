# Lesson 11: Exploratory Analysis for Stakeholders

## Learning outcomes
Apply the professional method, produce a project artefact and communicate decisions with evidence.

## 1. Core explanation
Exploratory data analysis for stakeholders begins with a decision question. Summarise the population, time period, key measures and important segments. Use appropriate comparisons and show denominators. A trend in counts may simply reflect growth in the population; rates can provide fairer comparison.

Distinguish descriptive findings from explanations. “Complaints increased by 15%” is descriptive. “The new system caused complaints to increase” requires evidence about alternative explanations and study design. Include uncertainty where relevant and avoid cherry-picking a favourable time window.

Present a small number of findings with supporting visuals and clear caveats. Put detailed methods and additional charts in an appendix. A stakeholder should understand what happened, why it matters, what remains uncertain and what decision is possible.

## 2. Worked example or template
Use the example in VS Code or adapt the structure to your project.

```python
import pandas as pd
import matplotlib.pyplot as plt

monthly = pd.DataFrame({
    "month": pd.date_range("2026-01-01", periods=6, freq="MS"),
    "active_users": [1000, 1100, 1250, 1400, 1500, 1600],
    "complaints": [30, 35, 39, 42, 51, 55]
})
monthly["complaints_per_1000"] = monthly["complaints"] / monthly["active_users"] * 1000
plt.plot(monthly["month"], monthly["complaints_per_1000"], marker="o")
plt.ylabel("Complaints per 1,000 active users")
plt.title("Complaint rate over time")
plt.show()
```

## 3. Professional application
Keep the artefact reproducible and honest. State the data source, time period, methods, your contribution and limitations. Do not publish confidential data or make unsupported performance claims.

## 4. Guided practice
Write three stakeholder findings from the chart and table. Explain why raw complaint counts and complaint rates tell different stories as active users grow.

## 5. Independent practice
Create or improve the corresponding project artefact. Ask another person to review it and record any unclear assumptions or missing instructions.

## 6. Knowledge check
1. What decision or audience does this artefact serve?
2. What evidence supports the claim?
3. Which limitations must be disclosed?
4. How can another person verify the work?

## Lesson summary
A professional portfolio demonstrates judgement, evidence, reproducibility and communication—not just familiarity with tools.