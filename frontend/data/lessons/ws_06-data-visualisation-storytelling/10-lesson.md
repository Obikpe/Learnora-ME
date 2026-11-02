# Lesson 10: Time-Series Visualisation

## Learning outcomes
Explain the visualisation method, implement the worked example in Python, interpret it and communicate its limitations.

## 1. Core explanation
Time-series data records observations in time order. Parse timestamps, sort rows, identify the time zone and decide the time granularity. A line chart is appropriate for a continuous sequence. Bars can be useful for discrete periods such as monthly totals. Missing periods must remain visible; do not connect across gaps as if observations were collected.

Trend is long-term direction; seasonality is a repeating pattern at a known frequency; noise is irregular variation. Rolling averages make a trend easier to see but smooth peaks and troughs and should not replace the original series. Year-over-year comparison can help separate seasonality from growth.

Do not aggregate before deciding what the question requires. Daily totals, weekly averages and monthly sums answer different questions. Rates need denominators: incidents per 1,000 active users may be more meaningful than raw incident counts when the user base changes.

## 2. Worked Python example
Run in VS Code. Install required packages with `python -m pip install pandas numpy matplotlib seaborn plotly`.

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.DataFrame({"date": pd.date_range("2026-01-01", periods=12, freq="D"),
                   "visits": [90,94,110,105,130,125,118,140,145,150,142,160]})
df["rolling_3"] = df["visits"].rolling(3, min_periods=1).mean()
fig, ax = plt.subplots(figsize=(8,4))
ax.plot(df.date, df.visits, label="Daily visits", alpha=.55)
ax.plot(df.date, df.rolling_3, label="3-day rolling mean")
ax.legend(); ax.set(title="Daily website visits", xlabel="Date", ylabel="Visits")
plt.show()
```

## 3. Interpretation and design checks
State the analytical question, population, variables, units and denominator. Check missingness and sample size. Distinguish observations from explanations and recommendations. Design for the actual audience and the size at which the visual will be viewed.

## 4. Guided practice
Create a 7-day rolling average. Explain why the first six values use fewer than seven observations when min_periods=1. Name one question that needs daily values and one better answered monthly.

## 5. Independent practice
Apply the lesson to a dataset. Create a chart or artefact, write a caption that states the main message and caveat, and ask another person to interpret it without your explanation.

## 6. Knowledge check
1. What question does this visual answer?
2. Which encoding or design choice supports the comparison?
3. What could mislead the audience?
4. What uncertainty or limitation must be disclosed?

## Lesson summary
Effective visual communication combines accurate encoding, clear context, audience-aware design and honest interpretation.