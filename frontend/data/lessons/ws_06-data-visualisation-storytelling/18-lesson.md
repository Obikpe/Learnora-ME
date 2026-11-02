# Lesson 18: Visualisation Portfolio Project

## Project brief

Create a reproducible visual analysis that answers a meaningful question and communicates the result to a defined audience. Use a public or synthetic dataset. If the dataset contains personal information, do not publish it; use an appropriately anonymised or synthetic alternative.

## Learning outcomes
Select a suitable dataset; formulate an analytical question; clean and inspect data; choose and build appropriate charts; explain findings; document limitations; and publish a reproducible project.

## Part A — Define the question
Write one main question and up to three supporting questions. Define the population, unit of analysis, time period and intended audience. Avoid questions so broad that they cannot be answered with the available variables.

## Part B — Inspect and prepare
Use Pandas to inspect dimensions, data types, missingness, duplicates and unusual values. Record cleaning decisions. Do not silently discard inconvenient records. Explain how each transformation affects the population and interpretation.

## Part C — Design the visual analysis
Create at least four charts serving different analytical purposes:
- One distribution chart.
- One comparison across categories or groups.
- One relationship chart.
- One time-series chart if the dataset has a meaningful time variable; otherwise justify an alternative.

Use clear labels, units, sensible scales and accessible contrast. Each chart should answer a specific question rather than repeat the same message.

## Part D — Interpret findings
For every chart, write:
1. What is visibly shown?
2. What pattern or difference is important?
3. What alternative explanation might exist?
4. What cannot be inferred?
5. What additional data would strengthen the analysis?

Do not claim causation from a descriptive chart.

## Part E — Deliver the project
Suggested structure:

```text
visualisation-project/
├── data/
├── notebooks/
├── src/
├── figures/
├── report.md
└── README.md
```

Keep raw data separate from processed data. Document the source, licence, date retrieved, packages and steps needed to reproduce the figures.

## Assessment rubric
| Area | Weight |
|---|---:|
| Question and audience definition | 10% |
| Data inspection and preparation | 15% |
| Chart choice and technical execution | 25% |
| Visual clarity and accessibility | 15% |
| Interpretation and storytelling | 20% |
| Reproducibility and limitations | 15% |

## Submission checklist
- [ ] The question and audience are explicit.
- [ ] Data source and licence are documented.
- [ ] Cleaning decisions are recorded.
- [ ] Each chart has a purpose, title, labels and units.
- [ ] Colour and scales do not mislead.
- [ ] Findings are supported by the displayed evidence.
- [ ] Limitations and alternative explanations are stated.
- [ ] Another learner can reproduce the project.

## Reflection
Which chart changed your understanding of the dataset most? Which design choice made the result clearer? What additional data would you request before recommending action?

## Course completion
A strong visualisation project is not a gallery of attractive charts. It is a transparent analytical argument: a clear question, appropriate evidence, careful design, honest interpretation and a reproducible workflow.