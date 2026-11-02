# Lesson 15: Time-Series Visualisation in Practice

## Learning outcomes
You should be able to parse and sort dates; choose a time axis; identify missing periods; resample observations; calculate rolling summaries; visualise seasonality and multiple series; and explain limits to trend interpretation.

## 1. What makes time-series data different?
A time series is a sequence of observations ordered in time. The interval may be seconds, days, months or years. Order and spacing matter. Common patterns include trend (long-term direction), seasonality (repeated pattern at a known interval), cycles (longer fluctuations without a fixed seasonal period) and noise (irregular variation).

A line chart is usually a good starting point because time has a natural order.

## 2. Parse dates correctly
Text dates can be ambiguous. Prefer ISO format YYYY-MM-DD or specify the expected format.

```python
import pandas as pd
df = pd.DataFrame({
    "date": ["2026-01-01", "2026-01-03", "2026-01-04"],
    "orders": [10, 15, 13]
})
df["date"] = pd.to_datetime(df["date"], errors="raise")
df = df.sort_values("date")
```

`errors="raise"` stops if a date cannot be parsed. Sorting ensures that a line does not jump backwards and forwards in time.

## 3. Plot actual time intervals
```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(df["date"], df["orders"], marker="o")
ax.set(title="Orders on recorded dates",
       xlabel="Date", ylabel="Orders")
fig.autofmt_xdate()
plt.show()
```

Matplotlib positions actual dates according to elapsed time. If a date is missing, the line spans the gap. Do not fill the gap with zero unless zero is truly the recorded value.

## 4. Resampling changes the time grain
Resampling aggregates observations into a new time frequency. Daily transactions can become monthly totals.

```python
daily = pd.DataFrame({
    "date": pd.date_range("2026-01-01", periods=60, freq="D"),
    "orders": range(20, 80)
}).set_index("date")

monthly = daily["orders"].resample("MS").sum()
print(monthly)
```

- `set_index("date")` makes date the index.
- `resample("MS")` groups records into month-start periods.
- `sum()` adds daily counts.

Choose the aggregation to match the measure: sum for counts or revenue over a period; mean for average daily temperature; last for an end-of-period balance. An average of daily averages may be misleading when daily sample sizes differ.

## 5. Rolling summaries
A rolling mean smooths short-term variation:

```python
daily["rolling_7"] = daily["orders"].rolling(
    window=7, min_periods=7
).mean()

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(daily.index, daily["orders"], alpha=0.45,
        label="Daily orders")
ax.plot(daily.index, daily["rolling_7"], linewidth=2.5,
        label="7-observation rolling mean")
ax.legend()
ax.set(xlabel="Date", ylabel="Orders",
       title="Daily orders and rolling mean")
plt.show()
```

`window=7` uses seven observations. `min_periods=7` requires all seven before producing a value, so the first six rows are missing. A rolling average reduces noise but can hide spikes and abrupt changes. State the window.

## 6. Calendar seasonality
You can derive calendar fields:
```python
daily = daily.reset_index()
daily["weekday"] = daily["date"].dt.day_name()
daily["month"] = daily["date"].dt.month_name()
```
Compare weekdays with a categorical chart if the question is “which weekday tends to be busier?” A line chart answers “how did the measure change through time?” Those are different questions.

## 7. Multiple time series
```python
import seaborn as sns
df = pd.DataFrame({
    "date": list(pd.date_range("2026-01-01", periods=4, freq="MS")) * 2,
    "region": ["North"] * 4 + ["South"] * 4,
    "revenue": [100, 120, 115, 140, 90, 95, 110, 125]
})
sns.lineplot(data=df, x="date", y="revenue",
             hue="region", marker="o")
plt.title("Monthly revenue by region")
plt.show()
```
Use consistent units and a shared scale. If there are many groups, use facets or focus on a few relevant series. When group sizes differ, consider rates per customer rather than raw totals.

## 8. Missing periods
A missing date is not the same as zero. It may indicate no activity, failed data collection, closure or an extraction problem. Create a complete date range to inspect gaps:

```python
full_index = pd.date_range(daily["date"].min(),
                           daily["date"].max(), freq="D")
daily = daily.set_index("date").reindex(full_index)
```

This inserts missing dates as missing values. Decide how to handle them based on the data-generating process. Do not automatically fill them with zero or interpolate.

## 9. Common mistakes
- Plotting unsorted dates.
- Treating missing dates as zero.
- Using the wrong resampling aggregation.
- Applying a rolling average without stating its window.
- Comparing groups with different denominators.
- Inferring seasonality from too short a period.
- Claiming a policy caused a change because the line shifted afterward.

## Guided practice
1. Parse dates and sort the dataset.
2. Plot daily values.
3. Resample to monthly totals.
4. Add a seven-observation rolling average.
5. Identify missing periods and decide whether they mean zero activity or unknown data.

## Independent practice
Use at least 60 time-ordered observations. Produce raw, resampled and smoothed charts. Explain the time grain, aggregation, missing periods and possible seasonal pattern. State one limitation.

## Knowledge check
1. Why parse dates?
2. What does resampling do?
3. How does a rolling average differ from a monthly total?
4. Why is a missing date not automatically zero?
5. What is seasonality?

## Lesson summary
Time-series visualisation requires correct date handling, time grain and missing-period interpretation. Resampling aggregates; rolling summaries smooth. Show or explain what smoothing hides, and do not infer cause from a trend alone.