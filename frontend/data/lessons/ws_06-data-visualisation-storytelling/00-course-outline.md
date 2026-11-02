# Data Visualisation with Matplotlib, Seaborn & Storytelling

**Course:** ws_06  
**Duration:** 12h (guided study allocation; learners should take additional practice time)  
**Lessons:** 20  
**Environment:** Python 3 in VS Code; Jupyter notebooks are optional, not required.

## Course purpose

This course teaches data visualisation as both an analytical skill and a communication skill. Learners begin with the purpose of visualisation and chart-reading, then learn Matplotlib and Seaborn carefully: imports and aliases, figures and axes, chart functions, arguments, labels, scales, legends, colour, annotations, statistical summaries and multi-panel layouts. Each chart family is taught with the question it answers, the data structure it requires, situations where it is appropriate, situations where it is misleading, and increasingly advanced examples.

The notes are intended for independent study. Every new term and code pattern must be explained. Code examples must include imports, realistic data, meaningful argument choices, expected interpretation and common mistakes. Learners should be able to run and modify examples in VS Code without needing a tutor to fill in missing steps.

## Learning journey: 20 lessons

1. **Visualisation Foundations and the Python Setup** — why charts work, chart grammar, data types, installing libraries, imports, aliases, and the Matplotlib Figure/Axes model.
2. **Matplotlib Line Charts** — `plot()`, ordered time data, markers, line styles, multiple series, limits, ticks, grids and reference lines.
3. **Matplotlib Bar Charts** — vertical and horizontal bars, grouped and stacked bars, sorting, labels, error bars and honest baselines.
4. **Histograms, Frequency and Density** — bins, bin width, frequency, density, cumulative distributions, KDE concepts and choosing distribution views.
5. **Scatter Plots and Relationships** — `scatter()`, marker properties, alpha, size, colour, overplotting, regression lines and correlation cautions.
6. **Pie, Donut and Part-to-Whole Charts** — angles, proportions, labels, wedges, stacked alternatives and when composition charts are defensible.
7. **Box Plots, Violin Plots and Category Distributions** — quartiles, IQR, whiskers, outliers, violin density, strip/swarm plots and group comparisons.
8. **Matplotlib Customisation and Annotation** — figure dimensions, axes, spines, ticks, formatters, legends, text, arrows, colour, styles, layout and export.
9. **Seaborn Foundations and Its Relationship with Matplotlib** — `import seaborn as sns`, themes, palettes, tidy/long-form data, axes-level versus figure-level functions and parameters.
10. **Seaborn Distribution Visualisation** — `histplot()`, `kdeplot()`, `ecdfplot()`, `displot()`, hue, bins, common_norm and distribution interpretation.
11. **Seaborn Categorical Visualisation** — `barplot()`, `countplot()`, `pointplot()`, `boxplot()`, `violinplot()`, `stripplot()`, `swarmplot()` and estimation versus raw counts.
12. **Seaborn Relational Visualisation** — `scatterplot()`, `lineplot()`, `relplot()`, hue, size, style, aggregation and uncertainty.
13. **Heatmaps, Correlation and Matrix Visuals** — pivot tables, correlation matrices, `heatmap()`, annotations, masks, colour scales and interpretation limits.
14. **Pairwise and Faceted Exploration** — `pairplot()`, `jointplot()`, `PairGrid`, `JointGrid`, `FacetGrid` and small multiples.
15. **Time-Series Visualisation in Practice** — date parsing, resampling, missing periods, rolling summaries, seasonality, multiple series and avoiding misleading time axes.
16. **Uncertainty, Error Bars and Statistical Estimation** — mean, median, spread, standard deviation, standard error, confidence intervals, bootstrap intuition and what error bars do not prove.
17. **Visualising Missing Data and Data Quality** — missingness maps, group-wise missingness, duplicates, outliers, invalid values and the danger of hiding data problems.
18. **Multi-Chart Figures and Dashboard Layouts** — subplots, shared axes, grids, consistent scales, chart hierarchy, KPI context, annotations and export-ready layouts.
19. **Visual Storytelling, Accessibility and Audience Communication** — narrative, annotation, colour accessibility, labels, source notes, caveats and audience-specific presentation.
20. **End-to-End Visualisation Portfolio Project** — question, data audit, chart selection, Matplotlib and Seaborn implementation, interpretation, report and reproducibility.

## Required teaching standard

For every chart family, explain:

- The analytical question it answers and the data shape it expects.
- The chart's visual grammar: what the x-axis, y-axis, marks, colours, sizes and facets represent.
- The main function and its important arguments, including what each argument changes.
- A complete runnable beginner example, then a more advanced example.
- How to read and interpret the output, including what cannot be concluded.
- When the chart is a good choice and when another chart is better.
- Common mistakes, misleading design choices and debugging tips.
- Guided practice, independent practice and knowledge checks.

## Python setup

Use Python 3 from VS Code. Create and activate a virtual environment, then install the libraries:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install numpy pandas matplotlib seaborn scipy
```

If PowerShell blocks activation, learners may run the environment's Python directly: `.venv\Scripts\python.exe -m pip install numpy pandas matplotlib seaborn scipy`. No database server or paid software is required.

## Assessment

Lessons contain short exercises and independent practice. The final project must include a clear question, data audit, justified chart choices, at least six complementary visualisations (including Matplotlib and Seaborn), written interpretations, limitations, and reproducible Python files. Attractive appearance alone does not earn credit: correctness, clarity, chart suitability, accessibility and honest interpretation matter.
