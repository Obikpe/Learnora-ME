# Lesson 8: Matplotlib Customisation, Annotation and Export

## Learning outcomes
You should be able to customise Figure and Axes properties; control ticks, tick labels and number formatting; create legends; add text, arrows and reference lines; manage colour and accessibility; arrange layout; and export figures reliably.

## 1. Why customisation matters

Customisation should make a chart easier to understand. It is not an invitation to decorate every chart. A professional visual should answer a question, make comparisons easy, identify units, provide context and remain readable at the size where it will be used.

The main Matplotlib structure is:

- Figure: overall canvas.
- Axes: one plotting region.
- Axis: the x or y scale and its ticks.
- Artist: a drawable object such as a line, text label, patch or legend.

You have already used the Figure and Axes model. This lesson develops control over those objects.

## 2. Figure size and resolution

```python
fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
```

`figsize` is width and height in inches. `dpi` means dots per inch and affects raster rendering. A larger figure is not automatically clearer; it must suit the destination. A chart for a report page may need a different aspect ratio from a slide.

## 3. Titles, labels and font sizes

```python
ax.set_title("Monthly revenue by region", fontsize=15, pad=12)
ax.set_xlabel("Month", fontsize=11)
ax.set_ylabel("Revenue (₦ thousands)", fontsize=11)
ax.tick_params(axis="both", labelsize=9)
```

- `fontsize` changes text size.
- `pad` adds spacing between title and axes.
- `tick_params()` controls tick marks and tick-label appearance.
- `axis="both"` applies to x and y.

A useful title states what is being measured and compared. Axis labels should include units. If values are in thousands, say so; do not leave readers to infer the scale.

## 4. Tick positions and number formatting

Ticks are the marks and labels along an axis. You can choose their positions:

```python
ax.set_yticks([0, 25, 50, 75, 100])
```

For more advanced control, Matplotlib provides tick formatters:

```python
from matplotlib.ticker import FuncFormatter

def as_currency_thousands(value, position):
    return f"₦{value:,.0f}k"

ax.yaxis.set_major_formatter(FuncFormatter(as_currency_thousands))
```

The formatter receives the numeric tick value and its position, then returns the label text. Do not format values as percentages unless the underlying values are proportions or percentages. If your data contains 0.25 to mean 25%, multiply by 100 in the label formatter or convert the data consistently.

## 5. Legends: explain multiple series

When plotting more than one series, provide a label:

```python
ax.plot(months, north, label="North")
ax.plot(months, south, label="South")
ax.legend(title="Region", loc="upper left", frameon=False)
```

- `title` gives the legend a heading.
- `loc` controls its placement.
- `frameon=False` removes the legend border.

A legend should not cover important data. Place it outside the axes when necessary using a suitable layout, or use direct labels on the lines if there are only a few series.

## 6. Annotations and text

Use `ax.text()` to place text at a coordinate. Use `ax.annotate()` when you want to connect text to a point:

```python
ax.annotate(
    "Highest recorded month",
    xy=("Jun", 175),
    xytext=("Apr", 190),
    arrowprops={"arrowstyle": "->", "linewidth": 1.2},
    fontsize=9
)
```

`xy` is the point being described; `xytext` is the text position. Annotations should explain a meaningful event, threshold or unusual value. Too many annotations compete for attention.

## 7. Reference lines and shaded regions

```python
ax.axhline(150, color="darkred", linestyle="--",
           label="Monthly target")
ax.axvspan("Mar", "Apr", color="gold", alpha=0.15,
           label="Campaign period")
```

- `axhline()` draws a horizontal reference line.
- `axvline()` draws a vertical reference line.
- `axhspan()` and `axvspan()` shade a horizontal or vertical interval.

A shaded period can identify a policy change or campaign window. It does not establish that the event caused a change in the measured variable.

## 8. Colour choices

Use colour to encode a meaningful distinction. A few principles:

- Use one consistent colour for one group across a report.
- Use sequential palettes for low-to-high quantities.
- Use diverging palettes when there is a meaningful midpoint.
- Use categorical palettes for unrelated categories.
- Do not rely on red versus green alone; some viewers cannot distinguish them easily.
- Ensure text and marks have sufficient contrast against the background.

Colour should reinforce the message, not become the message.

## 9. Styles and rcParams

Matplotlib styles provide coordinated defaults:

```python
plt.style.use("seaborn-v0_8-whitegrid")
```

A style can change fonts, backgrounds, grid lines and other defaults. Available style names can be inspected with:

```python
print(plt.style.available)
```

For more specific defaults, use `plt.rcParams`:

```python
plt.rcParams["figure.figsize"] = (8, 4)
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.labelsize"] = 11
```

These settings affect subsequent plots in the running Python process. Be careful when changing global defaults in a large project. A local Axes setting is often easier to reason about.

## 10. Layout: tight_layout and constrained layout

Overlapping labels make charts difficult to read. Create a figure with constrained layout:

```python
fig, ax = plt.subplots(figsize=(9, 5), layout="constrained")
```

Or call:

```python
fig.tight_layout()
```

These tools adjust spacing. They cannot solve every layout problem, especially when labels are extremely long or many axes are present. Rotate labels, increase figure size or redesign the chart when necessary.

## 11. Save the chart correctly

```python
fig.savefig("monthly_revenue.png", dpi=200, bbox_inches="tight")
fig.savefig("monthly_revenue.pdf", bbox_inches="tight")
```

- PNG is a raster image, useful for screens and documents.
- PDF is a vector format, useful for reports and print because lines and text can remain sharp when enlarged.
- `dpi` controls raster resolution.
- `bbox_inches="tight"` trims excess whitespace around the figure.

Save before or after `plt.show()` depending on the environment; a safe habit is to save using the Figure object before displaying it.

## 12. Complete polished chart

```python
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
revenue = [120, 135, 128, 150, 168, 175]
target = 160

fig, ax = plt.subplots(figsize=(9, 5), layout="constrained")
ax.plot(months, revenue, marker="o", linewidth=2.5,
        color="#2457A7", label="Revenue")
ax.axhline(target, color="#B23A48", linestyle="--",
           linewidth=1.5, label="Target")

ax.set_title("Revenue passed the monthly target in May",
             fontsize=15, loc="left")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue (₦ thousands)")
ax.yaxis.set_major_formatter(
    FuncFormatter(lambda value, position: f"₦{value:,.0f}k")
)
ax.set_ylim(0, 200)
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)
ax.annotate("First month above target",
            xy=("May", 168), xytext=("Mar", 190),
            arrowprops={"arrowstyle": "->"})
ax.legend(frameon=False)

fig.savefig("revenue_target.png", dpi=200, bbox_inches="tight")
plt.show()
```

This chart has a message-led title, labelled axes, units, a target line, an annotation and a saved output. The vertical range starts at zero to preserve the visual scale. The target line is meaningful only if the organisation genuinely uses that target.

## 13. Common mistakes

- Using a title that says only “Chart”.
- Leaving units off the axes.
- Choosing font sizes too small for the final output.
- Using a legend with unexplained abbreviations.
- Adding excessive arrows, colours and grid lines.
- Saving a low-resolution image for print.
- Forgetting to save the figure before closing the script.
- Formatting a number as currency or percentage when the underlying unit does not match.

## Guided practice

1. Add a title, labels and legend to a two-line chart.
2. Change tick formatting to currency.
3. Add a target line and annotate the first crossing.
4. Save both PNG and PDF.
5. View the saved file at its intended size and check readability.

## Independent practice

Create a polished chart from a real dataset. Include a meaningful title, units, source note, appropriate scale, accessible colour choices and one annotation that adds genuine context. Export to PNG and PDF. Ask another person what message they take from it and revise if the message is unclear.

## Knowledge check

1. What is the difference between `figsize` and `dpi`?
2. What does `ax.annotate()` provide beyond a title?
3. Why should a legend have meaningful labels?
4. When might PDF be preferable to PNG?
5. Why is colour accessibility part of chart quality?

## Lesson summary

Matplotlib customisation makes evidence understandable. Control titles, labels, ticks, legends, annotations, colour, layout and export deliberately. A polished chart is not the one with the most decoration; it is the one that makes the intended comparison clear and honest.