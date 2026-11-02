# Lesson 1: Visualisation Foundations and the Python Setup

## Learning outcomes
By the end of this lesson, you should be able to explain what visualisation does; identify the question, variables, units and observation represented by a chart; distinguish categorical and numerical data; install the course libraries in VS Code; explain Python imports and aliases; and create your first Matplotlib Figure and Axes.

## 1. What is data visualisation?

Data visualisation means representing information using visual marks such as points, lines, bars, areas and colours. A spreadsheet can show exact numbers, but a chart can make a pattern easier to notice. Imagine a table containing 365 daily sales values. Finding the busiest day by reading every row is slow. A chart can reveal weekday patterns, unusual spikes and periods of decline quickly.

Visualisation has two connected jobs:

- **Exploration:** the analyst investigates data, checks quality, looks for patterns and develops questions.
- **Explanation:** the analyst presents selected evidence so another person can understand a finding and make a decision.

A chart is not proof of a cause. If sales rise after an advert is launched, the chart shows that the two events occurred in that order. It does not, by itself, prove that the advert caused the rise. Other events, seasonality or changes in measurement may explain it.

## 2. Start with the data

A dataset is often arranged as a table. A **row** is one observation; a **column** is one variable. In a daily sales table, one row might represent one date, while columns might include date, orders, revenue and region.

Variables have different types:

- **Nominal categorical:** names without a natural order, such as region or payment method.
- **Ordinal categorical:** categories with an order, such as beginner, intermediate and advanced.
- **Discrete numerical:** countable values, such as number of orders.
- **Continuous numerical:** measured values that can take many possible values, such as time or weight.
- **Temporal:** dates and times, which have a meaningful chronological order.

Do not treat category codes as measurements. If North, South and West are encoded as 1, 2 and 3, the number 3 is not “three times” the number 1. Those codes are labels, not quantities.

## 3. Visual grammar: what does a chart use?

A chart uses **marks** (points, lines, bars, areas) and **channels** (position, length, angle, size, colour and shape) to represent data.

Position along a common scale is usually one of the easiest visual properties to compare. Bar length is also effective. Angle and area are harder to compare precisely, which is one reason pie charts become difficult when slices are similar. Colour hue is useful for distinguishing a few categories; lightness is more suitable for showing ordered magnitude.

Always ask: what does each axis mean? What does one mark represent? What is the unit? Which groups are included? What comparison should the viewer make?

## 4. Install Python libraries in VS Code

Open a project folder in VS Code. Open the integrated terminal using **Terminal → New Terminal**. Create a virtual environment:

```bash
python -m venv .venv
```

A virtual environment is an isolated Python installation for one project. It keeps the project's packages separate from other projects. On Windows PowerShell, activate it with:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

Install the libraries:

```bash
python -m pip install --upgrade pip
python -m pip install numpy pandas matplotlib seaborn scipy
```

- **NumPy** provides arrays and numerical operations.
- **Pandas** provides labelled tables called DataFrames.
- **Matplotlib** is a general plotting library.
- **Seaborn** builds statistical charts on top of Matplotlib.
- **SciPy** provides scientific and statistical functions used in some advanced examples.

If activation is blocked by a Windows execution policy, do not change system security settings just to follow this course. You can call the environment's Python directly: `.venv\Scripts\python.exe -m pip install numpy pandas matplotlib seaborn scipy`.

## 5. Understand imports and aliases

Python code uses libraries by importing them. Consider:

```python
import matplotlib.pyplot as plt
```

Read it from left to right:

- `import` tells Python to load a module.
- `matplotlib` is the library.
- `.pyplot` selects Matplotlib's pyplot module, which provides familiar plotting functions.
- `as` means “refer to this imported module using another name”.
- `plt` is the alias chosen for convenience.

The alias is not a special Python keyword and it is not compulsory. This is also valid:

```python
import matplotlib.pyplot
matplotlib.pyplot.plot([1, 2, 3], [2, 4, 3])
```

But repeatedly typing the longer name is inconvenient, so the common convention is `plt`. Similarly, Seaborn is conventionally imported as `sns`:

```python
import seaborn as sns
```

You could choose another alias, but using familiar conventions makes code easier for other Python users to read. An alias does not install a library; installation and importing are different operations.

## 6. Figure and Axes: the Matplotlib drawing model

A **Figure** is the entire drawing canvas. An **Axes** is an individual plotting area inside that canvas. A Figure can contain one Axes or many Axes.

The usual modern pattern is:

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
```

Here, `plt.subplots()` creates a Figure and an Axes and returns both. We assign them to `fig` and `ax`. The names are variables; you could call them something else, but these short names are common.

Use the Axes object to draw and customise the chart:

- `ax.plot(...)` draws a line.
- `ax.set_title(...)` sets the title.
- `ax.set_xlabel(...)` labels the horizontal axis.
- `ax.set_ylabel(...)` labels the vertical axis.
- `ax.grid(...)` adds grid lines.
- `ax.legend(...)` displays a legend when plotted series have labels.

Use the Figure object for whole-figure operations, such as saving or adjusting the overall layout:

- `fig.savefig(...)` saves the figure.
- `fig.tight_layout()` adjusts spacing so labels are less likely to overlap.

`plt.show()` displays the figure in a normal Python script. The object-oriented `fig, ax` approach is recommended because it gives you direct control, especially when a figure contains multiple charts.

## 7. Your first complete chart

Create a file named `first_chart.py` and run it in VS Code:

```python
import matplotlib.pyplot as plt

# Example: number of completed lessons per week
weeks = ["Week 1", "Week 2", "Week 3", "Week 4"]
completed = [12, 18, 15, 23]

# Create a canvas (Figure) and a plotting area (Axes).
fig, ax = plt.subplots(figsize=(8, 4))

# Draw bars on the Axes.
ax.bar(weeks, completed)

# Explain what the chart shows.
ax.set_title("Lessons completed each week")
ax.set_xlabel("Week")
ax.set_ylabel("Number of completed lessons")
ax.set_ylim(0, 25)

# Add a light horizontal grid to help compare bar heights.
ax.grid(axis="y", alpha=0.25)

# Keep the bars in front of the grid.
ax.set_axisbelow(True)

# Display the completed Figure.
plt.show()
```

The `figsize=(8, 4)` argument sets the figure width and height in inches. `ax.bar(x, height)` receives category labels and their values. `set_ylim(0, 25)` controls the visible vertical range. `grid(axis="y")` asks for horizontal grid lines only. `alpha` controls transparency: 0 is invisible and 1 is fully opaque.

## 8. When should you use a chart?

Start from the question, not from the chart you happen to like:

| Question | Common chart | Example |
|---|---|---|
| How does a measure change over time? | Line | Monthly revenue |
| Which categories are larger? | Bar | Sales by region |
| How are numerical values distributed? | Histogram | Exam scores |
| Do two numerical variables move together? | Scatter | Study hours and score |
| How is a whole divided into a few parts? | Pie or stacked bar | Small set of budget shares |
| How do groups' distributions differ? | Box or violin | Scores by class |
| Which cells in a matrix are high or low? | Heatmap | Correlations |

These are starting points, not rigid laws. Always consider the number of categories, sample size, measurement scale and audience.

## 9. Common beginner errors

- **ModuleNotFoundError:** the package may have been installed into a different Python environment. Check the interpreter selected in VS Code and install using that interpreter's `python -m pip`.
- **Using `plt` without importing it:** the alias only exists after the import statement runs.
- **Calling a method on the wrong object:** `ax.set_title()` belongs to an Axes; `fig.savefig()` belongs to a Figure.
- **Missing labels:** a chart without units or meaningful axis labels can be impossible to interpret.
- **Assuming the chart proves causation:** charts describe patterns; causal claims need an appropriate research design.

## 10. Guided practice

1. Change the weekly values and rerun the chart.
2. Change `figsize` to `(5, 5)`. What changes?
3. Remove `ax.set_ylim(0, 25)`. How does Matplotlib choose the visible range?
4. Change `alpha` from 0.25 to 1. What happens to the grid?
5. Explain in your own words what `plt`, `fig` and `ax` refer to.

## 11. Independent practice

Create a DataFrame with six months, monthly customer counts and monthly revenue. Choose one variable to visualise. Write down the analytical question before writing the code. Give the chart a meaningful title, axis labels and units. In a short paragraph, state one observation and one thing the chart cannot tell you.

## Knowledge check

1. What is the difference between a Figure and an Axes?
2. What does the `as plt` part of an import statement do?
3. Is `plt` a Python keyword? Explain.
4. Why should region codes not automatically be plotted as continuous numerical values?
5. Why is a chart not proof of causation?

## Lesson summary

A chart is a visual representation of data built for a question. Learn the data types and visual encodings first. In Matplotlib, a Figure is the canvas and an Axes is the plotting area. The common `plt` alias is simply a convenient name for `matplotlib.pyplot`; it is created by the import statement, not built into Python.