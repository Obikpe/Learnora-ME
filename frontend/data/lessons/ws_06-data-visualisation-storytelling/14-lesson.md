# Lesson 14: Interactive Visualisation Concepts

## Learning outcomes

By the end of this lesson, you should be able to explain filtering, hover, zoom and selection interactions; build a basic Plotly chart; design meaningful defaults and tooltips; and identify how interaction can hide context or distort denominators.

## 1. Core explanation
Interactive charts allow users to explore details through filtering, hovering, zooming and selecting. They are useful when an audience needs to inspect many categories or compare different segments. Interaction should answer a real question, not compensate for a confusing static chart.

A useful interactive design has clear defaults, visible filters, meaningful tooltips and a way to reset the view. Ensure users can understand the chart without hovering. Provide accessible labels and avoid relying only on colour. Large datasets may need aggregation or sampling to keep interaction responsive.

Interactive views can encourage selective exploration. If users can filter until a preferred pattern appears, explain that the display is exploratory and preserve context such as total population and date range. A dashboard should not hide missing categories or silently change denominators.

## 2. Worked Python example
Run in VS Code. Install required packages with `python -m pip install pandas numpy matplotlib seaborn plotly`.

```python
import plotly.express as px
import pandas as pd

df = pd.DataFrame({"month": ["Jan", "Feb", "Mar", "Apr"],
                   "region": ["North", "North", "South", "South"],
                   "sales": [120, 135, 90, 110]})
fig = px.line(df, x="month", y="sales", color="region",
              markers=True, title="Monthly sales by region")
fig.show()
```

## 3. Interpretation and design checks
State the analytical question, population, variables, units and denominator. Check missingness and sample size. Distinguish observations from explanations and recommendations. Design for the actual audience and the size at which the visual will be viewed.

## 4. Guided practice
Add a region filter or hover tooltip. Decide which information should remain visible without interaction. Explain how an interactive filter could mislead if the denominator is not shown.

## 5. Independent practice
Apply the lesson to a dataset. Create a chart or artefact, write a caption that states the main message and caveat, and ask another person to interpret it without your explanation.

## 6. Knowledge check
1. What question does this visual answer?
2. Which encoding or design choice supports the comparison?
3. What could mislead the audience?
4. What uncertainty or limitation must be disclosed?

## Lesson summary
Effective visual communication combines accurate encoding, clear context, audience-aware design and honest interpretation.