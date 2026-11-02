# Lesson 15: Dashboard Design and Layout

## Learning outcomes
Explain the visualisation method, implement the worked example in Python, interpret it and communicate its limitations.

## 1. Core explanation
A dashboard is a coordinated set of views for monitoring or decision support. Begin with the audience and decisions, then select a small number of metrics. Place the most important status or trend first, supporting breakdowns below and detailed records last. Use consistent definitions and time filters across charts.

KPI cards need context: current value, comparison period, target and direction. A red/green colour alone may not be accessible or meaningful. Filters should be obvious and consistent. Avoid overcrowding, excessive chart types and decorative gauges. Make refresh time and data coverage visible.

A dashboard is not a report that answers every possible question. Use it for recurring monitoring; use a separate analysis for deep investigation. Test it with real users and observe whether they can answer the intended questions without explanation.

## 2. Worked Python example
Run in VS Code. Install required packages with `python -m pip install pandas numpy matplotlib seaborn plotly`.

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(10, 7))
axes[0, 0].text(.5, .5, "KPI: Active users\n1,240 (+8%)", ha="center", va="center")
axes[0, 1].plot([100, 110, 108, 125, 132])
axes[0, 1].set_title("Weekly active users")
axes[1, 0].bar(["North", "South", "East"], [42, 35, 23])
axes[1, 0].set_title("Users by region")
axes[1, 1].text(.5, .5, "Data refreshed: 02 Nov 2026", ha="center", va="center")
axes[1, 1].axis("off")
plt.tight_layout(); plt.show()
```

## 3. Interpretation and design checks
State the analytical question, population, variables, units and denominator. Check missingness and sample size. Distinguish observations from explanations and recommendations. Design for the actual audience and the size at which the visual will be viewed.

## 4. Guided practice
Sketch a dashboard for a training manager. Define three KPIs, comparison periods, filter behaviour, refresh frequency and the decision each visual supports.

## 5. Independent practice
Apply the lesson to a dataset. Create a chart or artefact, write a caption that states the main message and caveat, and ask another person to interpret it without your explanation.

## 6. Knowledge check
1. What question does this visual answer?
2. Which encoding or design choice supports the comparison?
3. What could mislead the audience?
4. What uncertainty or limitation must be disclosed?

## Lesson summary
Effective visual communication combines accurate encoding, clear context, audience-aware design and honest interpretation.