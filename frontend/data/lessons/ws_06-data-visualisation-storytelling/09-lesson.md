# Lesson 9: Seaborn Foundations and Its Relationship with Matplotlib

## Learning outcomes
You should be able to explain what Seaborn adds to Matplotlib; import it using the conventional `sns` alias; understand its relationship with Matplotlib Axes and Figures; distinguish axes-level and figure-level functions; prepare tidy data; and use themes, palettes, hue and common plotting arguments.

## 1. What is Seaborn?

Matplotlib is a flexible plotting library. It gives you fine control over the figure and every plotting element. Seaborn is a statistical visualisation library built on top of Matplotlib. It provides convenient functions for common statistical charts and works naturally with Pandas DataFrames.

Seaborn does not replace Matplotlib. They work together:
- Seaborn makes many statistical charts easier to create.
- Matplotlib provides the underlying Figure and Axes and gives detailed control over the final result.
- You can create a Matplotlib Axes, ask Seaborn to draw on it, then customise the chart with Matplotlib methods.

This is why a Seaborn chart can use `ax.set_title()`, `ax.set_xlabel()` and `fig.savefig()`.

## 2. Importing Seaborn with the alias sns

The standard import is:

```python
import seaborn as sns
```

This means: import the Seaborn library and refer to it using the short name `sns`. The alias is a convention, not a required name and not a special Python keyword. You could write `import seaborn` and then call `seaborn.histplot()`, but `sns` is widely recognised.

A typical visualisation script imports the main libraries:

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
```

The aliases `np`, `pd`, `plt` and `sns` are common conventions:
- `np`: NumPy.
- `pd`: Pandas.
- `plt`: Matplotlib pyplot.
- `sns`: Seaborn.

If Python reports `NameError: name 'sns' is not defined`, check that the import statement has run in the current script or notebook.

## 3. Tidy data: the structure Seaborn likes

Seaborn works particularly well with **tidy data**. In a tidy table:
- each row is one observation;
- each column is one variable;
- each cell contains one value.

Example:

| learner | class | study_hours | score |
|---|---|---:|---:|
| A01 | A | 2 | 55 |
| A02 | A | 4 | 68 |
| B01 | B | 3 | 62 |
| B02 | B | 5 | 77 |

The column names describe variables. This structure makes it easy to tell Seaborn which variable belongs on x, y, colour or marker size.

A wide table may have one column per group. It can be useful for some Matplotlib operations, but Seaborn often becomes easier when data is converted to long/tidy form.

## 4. Your first Seaborn chart

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.DataFrame({
    "class": ["A", "A", "A", "B", "B", "B"],
    "study_hours": [2, 3, 4, 2, 4, 5],
    "score": [55, 61, 68, 52, 70, 77]
})

sns.scatterplot(data=df, x="study_hours", y="score",
                hue="class", s=90)
plt.title("Study hours and score by class")
plt.xlabel("Study hours per week")
plt.ylabel("Score")
plt.show()
```

Read the arguments:
- `data=df`: use the DataFrame as the source.
- `x="study_hours"`: use the named column for horizontal position.
- `y="score"`: use the named column for vertical position.
- `hue="class"`: colour points according to the class category.
- `s=90`: set marker size.

This is different from manually passing arrays to Matplotlib. Seaborn can look up columns by name using the `data`, `x` and `y` arguments.

## 5. The Axes-level and Figure-level distinction

Seaborn functions fall into two broad groups.

**Axes-level functions** draw onto one Matplotlib Axes. Examples include:
- `sns.scatterplot()`
- `sns.lineplot()`
- `sns.histplot()`
- `sns.boxplot()`
- `sns.violinplot()`
- `sns.heatmap()`

They accept `ax=` so you can choose where the chart appears:

```python
fig, ax = plt.subplots(figsize=(7, 4))
sns.histplot(data=df, x="score", bins=5, ax=ax)
ax.set_title("Score distribution")
plt.show()
```

**Figure-level functions** manage an entire Figure and can create multiple panels. Examples include:
- `sns.relplot()`
- `sns.displot()`
- `sns.catplot()`
- `sns.pairplot()`
- `sns.jointplot()`

They usually return a Seaborn grid object rather than a single Axes. You customise the returned object through its methods and its underlying axes. Do not pass an `ax=` argument to a figure-level function unless its documentation specifically supports it.

## 6. Themes with set_theme()

A theme changes the default appearance of Seaborn charts:

```python
sns.set_theme(style="whitegrid", context="notebook",
              palette="deep")
```

- `style`: background and grid style. Common choices include `"darkgrid"`, `"whitegrid"`, `"dark"`, `"white"` and `"ticks"`.
- `context`: scales text and elements for a use case, such as `"paper"`, `"notebook"`, `"talk"` or `"poster"`.
- `palette`: default colour palette.

A theme is a starting point. You still need to check contrast, labels and readability. Themes affect subsequent charts in the current Python process.

## 7. Colour palettes and hue

The `hue` argument maps a variable to colour. If the variable is categorical, Seaborn generally uses different category colours. If the variable is numerical, use a sequential palette and provide a meaningful scale where needed.

```python
sns.set_theme(style="whitegrid", palette="colorblind")
sns.scatterplot(data=df, x="study_hours", y="score",
                hue="class", style="class", s=100)
plt.show()
```

Here, both colour and marker style distinguish the classes. This can improve accessibility for viewers who cannot distinguish all colours. Do not encode too many categories; the legend becomes difficult to read.

Useful palette families:
- **Qualitative:** unrelated categories, e.g. `"deep"`, `"Set2"`, `"colorblind"`.
- **Sequential:** ordered low-to-high values, e.g. `"viridis"`, `"mako"`, `"rocket"`.
- **Diverging:** values around a meaningful midpoint, e.g. below/above zero.

## 8. Common arguments you will see repeatedly

- `data`: DataFrame or data structure containing variables.
- `x`, `y`: columns mapped to axes.
- `hue`: variable mapped to colour.
- `style`: variable mapped to marker or line style.
- `size`: variable mapped to marker size.
- `palette`: colour palette.
- `ax`: Matplotlib Axes on which to draw.
- `col` and `row`: variables used to create facets/panels in figure-level functions.
- `legend`: whether to show a legend.
- `height` and `aspect`: size controls in many figure-level functions.

Not every function accepts every argument. Read the function's help or documentation rather than assuming all arguments work everywhere:

```python
help(sns.scatterplot)
```

In VS Code, place the cursor inside the function call and use editor hints, or inspect the official function documentation. Error messages often tell you when an argument is unsupported.

## 9. Combine Seaborn and Matplotlib

```python
fig, ax = plt.subplots(figsize=(8, 5))
sns.scatterplot(data=df, x="study_hours", y="score",
                hue="class", s=100, ax=ax)
ax.set_title("Learner study hours and scores")
ax.set_xlabel("Study hours per week")
ax.set_ylabel("Assessment score")
ax.grid(alpha=0.2)
fig.savefig("study_score.png", dpi=180, bbox_inches="tight")
plt.show()
```

Seaborn draws the points; Matplotlib controls the axes labels, grid, Figure and saved file. This combination is common in real analysis.

## 10. Common mistakes

- Thinking `sns` is built into Python rather than created by an import.
- Forgetting that Seaborn is installed separately.
- Passing a column name without `data=df` when the function expects a DataFrame.
- Confusing axes-level and figure-level functions.
- Trying to pass `ax=` to a figure-level function that manages its own grid.
- Using a qualitative palette for a continuous numeric scale.
- Creating a chart without checking category order or missing values.

## Guided practice

1. Import Seaborn as `sns` and create a DataFrame.
2. Make a scatter plot with `hue="class"`.
3. Change the theme from `whitegrid` to `ticks`.
4. Draw the same chart on a Matplotlib Axes using `ax=ax`.
5. Use `help(sns.scatterplot)` to inspect its parameters.

## Independent practice

Create a tidy DataFrame with a numerical measure, a numerical second variable and a categorical group. Make a Seaborn chart, then customise it with Matplotlib. Explain the purpose of `data`, `x`, `y`, `hue`, `palette` and `ax`.

## Knowledge check

1. What does `import seaborn as sns` mean?
2. How are Seaborn and Matplotlib related?
3. What is tidy data?
4. What is the difference between an axes-level and a figure-level function?
5. Why should a numerical hue variable use a sequential palette?

## Lesson summary

Seaborn simplifies statistical visualisation while relying on Matplotlib for drawing. The conventional alias is `sns`. Learn the tidy-data structure, use `data`, `x`, `y` and `hue` to map variables, distinguish axes-level from figure-level functions, and combine Seaborn with Matplotlib for precise control.