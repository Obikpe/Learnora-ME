# Lesson 20: End-to-End Visualisation Portfolio Project

## Project purpose
Create a reproducible visual analysis demonstrating that you can choose, build, customise and interpret charts using Matplotlib and Seaborn. The goal is not to produce the largest number of charts. The goal is to answer a meaningful question with suitable visuals and honest interpretation.

## Learning outcomes
Define a question and audience; inspect and prepare a dataset; select appropriate chart forms; create at least six complementary visualisations; explain function arguments and design choices; interpret patterns without unsupported causal claims; and publish a reproducible portfolio artefact.

## 1. Choose a dataset
Use a public dataset with a clear source and licence, or create synthetic data. Do not publish private or personally identifiable records. Choose data with at least one numerical and one categorical variable. A time variable is useful but not compulsory. Record the source, licence, retrieval date, row count, column definitions and intended population.

## 2. Define the analytical question
Write one main question and up to three supporting questions. Examples:
- How did monthly sales change, and which region contributed most?
- How are learner scores distributed, and do distributions differ by cohort?
- Which numerical measures are associated, and what further evidence is needed?

Define the unit of observation, population, period, units and audience.

## 3. Audit and prepare the data
Use Pandas to inspect shape, columns, data types, missing values, duplicates, invalid values, category consistency, time coverage and unusual observations. Preserve raw data. Create a separate cleaned DataFrame and document transformations. Do not remove outliers or fill missing values without a reason.

## 4. Build at least six complementary charts
Include at least six charts, selected from:
1. Matplotlib line chart for an ordered sequence, if the data supports it.
2. Matplotlib vertical or horizontal bar chart for category comparison.
3. Histogram for a numerical distribution.
4. Scatter plot for a relationship between numerical variables.
5. Seaborn categorical chart such as box, violin, count or bar plot.
6. Seaborn heatmap or faceted chart if the structure supports it.

Do not force an unsuitable chart type. If the data does not support a time series, explain why a line chart would be inappropriate and choose a valid alternative. Assessment rewards justified choices, not mechanical chart use.

## 5. Explain every chart
For each visual, document:
- The question it answers.
- What one row and one mark represent.
- Variables and units.
- Why the chart is suitable.
- The important function and arguments used.
- What the chart visibly shows.
- What cannot be concluded.
- One alternative explanation or limitation.

Include at least one advanced feature: moving average, grouped/stacked bars, hue mapping, facets, colour bar, annotation, confidence interval or justified reference line.

## 6. Suggested project structure
```text
visualisation-portfolio/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   └── exploration.ipynb
├── src/
│   └── visualise.py
├── figures/
├── report.md
├── requirements.txt
└── README.md
```

Do not commit confidential data, credentials or private records. If data is restricted or large, document how to obtain it or use a safe sample.

## 7. Reproducibility
A simple requirements file may contain:
```text
numpy
pandas
matplotlib
seaborn
scipy
```

A reviewer should be able to create an environment, install packages, run the script or notebook and reproduce the figures. Use relative file paths where practical and explain where the dataset belongs.

## 8. Report structure
Your `report.md` should contain:
1. Project title and summary.
2. Problem and audience.
3. Dataset source, licence and data dictionary.
4. Data-quality checks and cleaning decisions.
5. Analytical questions.
6. Each chart with interpretation and limitations.
7. Overall findings and proportionate recommendations.
8. Additional data or analysis needed.
9. Reproduction instructions.

## 9. Assessment rubric

| Area | Weight |
|---|---:|
| Question, audience and data understanding | 10% |
| Data inspection and preparation | 15% |
| Chart selection and statistical correctness | 20% |
| Matplotlib implementation and customisation | 15% |
| Seaborn implementation and interpretation | 15% |
| Accessibility, clarity and storytelling | 10% |
| Reproducibility, documentation and limitations | 15% |

## 10. Final submission checklist
- [ ] Question, population, unit and audience are explicit.
- [ ] Data source and licence are recorded.
- [ ] Data types, missingness and duplicates were inspected.
- [ ] Cleaning decisions are documented.
- [ ] At least six suitable charts are included.
- [ ] Matplotlib and Seaborn are both used.
- [ ] Every chart has a meaningful title, labels and units.
- [ ] Every chart has an interpretation and limitation.
- [ ] Colour, scales and annotations do not mislead.
- [ ] No unsupported causal claim is made.
- [ ] Code and dependencies are documented.
- [ ] Another learner can reproduce the output.

## Reflection
Which chart revealed the most important pattern? Which chart choice was difficult, and what alternatives did you consider? Which function arguments had the greatest effect on readability? What additional evidence would you collect before recommending action?

## Course completion
A complete visualisation workflow moves from a question to a chart, explains why the chart is suitable, states what the visual shows and cannot prove, and reproduces the output from documented code. A portfolio demonstrates reasoning, not merely a gallery of colourful charts.