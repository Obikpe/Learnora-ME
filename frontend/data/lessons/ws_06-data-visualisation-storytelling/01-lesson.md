# Lesson 1: Why Data Visualisation Matters

## Learning outcomes
By the end of this lesson, you should be able to explain why analysts visualise data, distinguish exploratory from explanatory visualisation, match a chart to a question, and describe a chart without making unsupported claims.

## 1. Why visualise data?
A table is excellent when a reader needs exact values. A chart is useful when the reader needs to notice a pattern quickly: a trend, comparison, cluster, unusual value or relationship. Visualisation is not decoration added after analysis. It is a way to inspect evidence, test questions and communicate findings.

A chart maps data values to visual properties. Position along a common scale is usually easiest to compare accurately; length is also effective. Area, angle and colour intensity are harder to estimate, so use them carefully. A visual can reveal a pattern, but it cannot prove why the pattern occurred.

Suppose a training manager asks whether weekly attendance is improving. A list of twelve percentages provides exact values. A line chart makes direction and fluctuations easier to see. If weeks are not equally spaced, use actual dates on the x-axis rather than pretending the intervals are equal.

## 2. Two purposes: exploration and explanation
Exploratory visualisation is for the analyst. You try different views, inspect anomalies, check distributions and ask follow-up questions. Explanatory visualisation is for an audience. You select a defensible message, remove distractions and show enough context to support the conclusion.

Do not present an exploratory chart as if it were a final finding. Exploration often involves many comparisons. If you repeatedly inspect a dataset until something looks significant, chance patterns can appear. Confirm important findings with appropriate statistical methods and, where possible, new data.

## 3. Worked example: attendance over time
The following dataset has one row per week. The attendance rate is stored as a proportion between zero and one. The y-axis is deliberately fixed from zero to one so the percentage scale is not visually exaggerated.

```python
import pandas as pd
import matplotlib.pyplot as plt

attendance = pd.DataFrame({
    "week": pd.date_range("2026-01-05", periods=6, freq="W-MON"),
    "attendance_rate": [0.72, 0.75, 0.71, 0.79, 0.82, 0.80]
})

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(attendance["week"], attendance["attendance_rate"], marker="o")
ax.set_title("Weekly learner attendance")
ax.set_xlabel("Week beginning")
ax.set_ylabel("Attendance rate")
ax.set_ylim(0, 1)
ax.grid(axis="y", alpha=0.25)
fig.autofmt_xdate()
plt.show()
```

Read the chart in three passes:
1. **Direction:** attendance rises overall from 72% to 80%, although it falls in week three and week six.
2. **Variation:** the values are not steadily increasing; there are short-term fluctuations.
3. **Limit:** six observations are too few to establish a durable trend or explain the cause of the changes.

A precise interpretation is: “Attendance ended at 80%, eight percentage points above the first observation, with fluctuations during the period.” Avoid saying that a new policy caused the increase unless the study design supports a causal conclusion.

## 4. A practical chart-reading framework
Before creating or interpreting a chart, identify:
- **Observation:** what does one row represent?
- **Measure:** what quantity or category is being shown?
- **Population:** which people, events or objects are included?
- **Time window:** when were the observations collected?
- **Scale:** what do the axes and units mean?
- **Comparison:** what should the reader compare?
- **Limitation:** what does the chart not establish?

These questions prevent common errors such as confusing counts with rates. For example, a region with more customers may have more complaints simply because it serves more customers. A complaint rate per 1,000 customers may be the fairer comparison.

## 5. Guided practice
Change the six attendance values and rerun the chart. Find the week with the lowest rate. Then create a small table containing the same dates and values. Decide which format is better for (a) noticing the overall pattern and (b) retrieving the exact rate for a particular week. Explain your decision.

## 6. Independent practice
Create a dataset with eight monthly values for a measure you understand, such as orders, revenue or learner completion. Plot it over time. Write a three-sentence interpretation that includes the starting value, ending value, overall direction and one limitation. Do not claim that one variable caused another merely because the chart appears to move with it.

## 7. Knowledge check
1. When is a table more useful than a chart?
2. What is the difference between exploratory and explanatory visualisation?
3. Why does a chart reveal a pattern but not necessarily its cause?
4. Why can a count be misleading when groups have different population sizes?

## Lesson summary
Visualisation helps analysts inspect patterns and helps audiences understand evidence. A sound chart starts with a clear question, represents the data honestly, labels its scales and units, and is interpreted with appropriate caution.