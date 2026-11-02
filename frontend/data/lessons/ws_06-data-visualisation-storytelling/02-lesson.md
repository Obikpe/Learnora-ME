# Lesson 2: Matplotlib Line Charts

## Learning outcomes
You should be able to explain when a line chart is suitable; create one with `ax.plot()`; control x and y values, markers, line styles, widths, colours and labels; plot multiple series; format dates and ticks; add reference lines; and avoid misleading time-series displays.

## 1. What a line chart communicates

A line chart connects ordered observations. The line helps the eye follow how a value changes as x changes. It is especially useful for time series: daily temperatures, monthly revenue, weekly attendance or yearly population.

The horizontal axis usually represents time or another ordered numerical scale. The vertical axis represents the measured quantity. The connected line suggests continuity or an ordered progression. Do not connect unrelated categories merely because they can be placed in a list.

A line chart is appropriate when:
- x has a natural order, especially time;
- the sequence between observations matters;
- the reader needs to see direction, turning points or fluctuations.

A line chart is often inappropriate when:
- x is a set of unrelated categories with no natural order;
- connecting observations suggests continuity that does not exist;
- there are so many overlapping series that the lines become unreadable.

## 2. The basic function: ax.plot()

The general form is:

```python
ax.plot(x_values, y_values, format_or_style_options)
```

- `x_values`: positions along the horizontal axis.
- `y_values`: values to plot vertically.
- `color`: line colour.
- `linestyle`: solid, dashed, dotted or dash-dot pattern.
- `linewidth`: thickness of the line.
- `marker`: symbol drawn at each observed point.
- `markersize`: marker size.
- `label`: name used in the legend.
- `alpha`: transparency, from 0 (invisible) to 1 (opaque).

The x and y sequences must have compatible lengths. If there are six dates, there must be six corresponding measurements.

## 3. First line chart, explained

```python
import matplotlib.pyplot as plt

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
revenue = [120, 135, 128, 150, 168, 175]

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(months, revenue, marker="o", color="steelblue",
        linestyle="-", linewidth=2, markersize=7)

ax.set_title("Monthly revenue")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue (thousand naira)")
ax.grid(axis="y", alpha=0.3)
plt.show()
```

The string `"o"` asks Matplotlib to draw circular markers at observations. `"-"` means a solid line. `linewidth=2` makes the connecting line thicker than the default. The chart shows revenue increasing overall, with a small decline from February to March.

Markers are useful when you want the reader to see the actual observations. For very dense daily data, markers can clutter the figure; use a line without markers or display a shorter time window.

## 4. Important line styles and markers

Common line styles:

- `"-"`: solid line.
- `"--"`: dashed line.
- `":"`: dotted line.
- `"-."`: dash-dot line.
- `"None"` or `linestyle="None"`: no connecting line.

Common markers include `"o"` circle, `"s"` square, `"^`` triangle, `"D"` diamond, `"x"` x mark and `"+"` plus mark. Use a small number of styles consistently. Too many colours and markers make the chart harder to decode.

## 5. Plotting more than one series

A common analytical question is whether two groups follow the same pattern. Draw one line per group and label each line:

```python
import matplotlib.pyplot as plt

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
north = [120, 135, 128, 150, 168, 175]
south = [100, 108, 115, 112, 125, 139]

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(months, north, marker="o", label="North")
ax.plot(months, south, marker="s", linestyle="--", label="South")

ax.set(title="Monthly revenue by region",
       xlabel="Month", ylabel="Revenue (thousand naira)")
ax.legend(title="Region")
ax.grid(axis="y", alpha=0.25)
plt.show()
```

Each call to `ax.plot()` adds another series to the same Axes. The `label` argument stores a human-readable name. `ax.legend()` displays those names. Without labels, the legend cannot explain which line represents which region.

When many groups overlap, consider small multiples (one panel per group), a selected subset, or a table. Do not force ten or twenty lines into one crowded chart.

## 6. Control the visible range and ticks

- `ax.set_xlim(left, right)` sets the horizontal range.
- `ax.set_ylim(bottom, top)` sets the vertical range.
- `ax.set_xticks(...)` selects tick positions.
- `ax.set_xticklabels(...)` supplies displayed labels (use carefully with matching tick positions).
- `ax.tick_params(axis="x", rotation=45)` rotates tick labels.
- `ax.grid(axis="y")` adds horizontal grid lines.

A truncated y-axis can exaggerate small movements. A line chart does not always need to begin at zero, but the axis range must be visible and the choice should not exaggerate the message. For a bar chart, zero is usually essential because bar length encodes magnitude.

## 7. Reference lines and annotations

A reference line adds a target or benchmark:

```python
target = 160
ax.axhline(target, color="darkred", linestyle="--",
           linewidth=1.5, label="Target: 160")
ax.legend()
```

`ax.axhline()` draws a horizontal line at a y value. `ax.axvline()` draws a vertical line at an x value. A reference line should have a meaningful explanation. Do not add a target just to decorate the chart.

Use `ax.annotate()` to explain a particular point:

```python
ax.annotate("Target first exceeded",
            xy=("May", 168),
            xytext=("Mar", 185),
            arrowprops={"arrowstyle": "->"})
```

The `xy` argument is the point being annotated. `xytext` is where the annotation text is placed. The arrow connects the text to the point.

## 8. Real dates on the x-axis

For time series, actual date values are better than labels such as "Day 1", "Day 2" when intervals are irregular. Pandas can create and parse dates:

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.DataFrame({
    "date": pd.to_datetime(["2026-01-01", "2026-01-04",
                            "2026-01-10", "2026-01-11"]),
    "orders": [20, 27, 22, 31]
})

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(df["date"], df["orders"], marker="o")
ax.set(title="Orders on recorded dates",
       xlabel="Date", ylabel="Orders")
fig.autofmt_xdate()
plt.show()
```

Notice that the dates are not equally spaced. Matplotlib positions them according to elapsed time. This is more honest than treating the four observations as equally spaced categories.

## 9. Advanced example: trend and moving average

A moving average smooths short-term fluctuations by averaging nearby observations. It can help reveal a broad trend, but it also hides detail and depends on the chosen window.

```python
import pandas as pd
import matplotlib.pyplot as plt

daily = pd.DataFrame({
    "date": pd.date_range("2026-01-01", periods=14, freq="D"),
    "orders": [10, 12, 9, 15, 13, 14, 18, 16, 15, 19, 17, 21, 20, 23]
})
daily["moving_average_3"] = daily["orders"].rolling(
    window=3, min_periods=1
).mean()

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(daily["date"], daily["orders"], marker="o",
        alpha=0.55, label="Daily orders")
ax.plot(daily["date"], daily["moving_average_3"],
        linewidth=2.5, label="3-day moving average")
ax.set(title="Daily orders and a 3-day moving average",
       xlabel="Date", ylabel="Orders")
ax.legend()
fig.autofmt_xdate()
plt.show()
```

The rolling window of 3 means each displayed average uses up to three consecutive observations. At the beginning, `min_periods=1` allows an average to be calculated with fewer than three values. Explain this choice; otherwise readers may assume every point uses a full three-day window.

## 10. Common mistakes

- Plotting unsorted dates: the line may move backwards and forwards in time. Sort by date first.
- Treating missing dates as zero: no record is not necessarily zero activity.
- Connecting unrelated categories: this implies a sequence that may not exist.
- Overloading the chart with series: use facets or a smaller selection.
- Hiding the axis range: always label units and inspect whether the range exaggerates a change.
- Calling a moving average the original data: show raw observations as context when possible.

## Guided practice

1. Recreate the first example with square markers and a dashed line.
2. Add a second region and a legend.
3. Add a target line at 160 and annotate the first month that exceeds it.
4. Remove the markers. Which version is easier to read with 100 daily observations?
5. Change the date sequence to include gaps. Explain why actual dates matter.

## Independent practice

Use at least 12 monthly observations. Create a line chart of one measure and, if appropriate, a second group. Add a target or benchmark only if it has a real meaning. Write a paragraph describing direction, fluctuations, unusual points and limitations. Explain why a line chart is more suitable than a bar chart—or justify the reverse.

## Knowledge check

1. What does `ax.plot(x, y)` do?
2. What is the difference between `marker` and `linestyle`?
3. Why must time-series data be sorted by date?
4. What does `rolling(window=3).mean()` calculate?
5. Why can a moving average hide important information?

## Lesson summary

Line charts show ordered change. Matplotlib's `ax.plot()` connects x and y observations; arguments such as `marker`, `linestyle`, `linewidth`, `label` and `alpha` control the display. Use real dates for time series, explain reference lines and moving averages, and never confuse a visible trend with proof of its cause.