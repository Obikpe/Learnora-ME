# Lesson 9: Writing Clear READMEs and Documentation

## Learning outcomes

By the end of this lesson, you should be able to Write a README that explains the problem, data source, environment, reproduction steps, methods, findings and limitations; and make the project understandable to a new reviewer.

## 1. Core explanation
A README is the entry point for a project. It should explain the problem, why it matters, the data source and licence, how to set up the environment, how to reproduce the analysis, what was found and what the limitations are. A reader should not need to inspect every notebook to understand the project.

Use a clear hierarchy: project overview, question, data, methods, results, how to run, repository structure and limitations. Include screenshots or figures only when they clarify findings. Provide links to reports and notebooks. Avoid unexplained acronyms and claims such as “highly accurate” without a metric and evaluation context.

Documentation must match the current code. If a script or dataset changes, update the README. Include data dictionaries for non-obvious fields and explain preprocessing decisions that materially affect the result.

## 2. Worked example or template
Use the example as a starting point and adapt it to your own project. Python examples run in VS Code; shell commands should be entered in the VS Code terminal.

```python
# Project README outline
# Project title
## Problem and objective
## Data source, licence and coverage
## Repository structure
## Environment setup
## How to reproduce
## Methods and evaluation
## Key findings
## Limitations and ethical considerations
## Contact or contribution guidance
```

## 3. Professional application
Keep claims evidence-based. Document sources, assumptions, licences, decisions and limitations. A portfolio project should be understandable and reproducible without access to private data or undocumented local files.

## 4. Guided practice
Write a README for a project you have completed. Ask a peer to reproduce one result using only the README. Record every instruction they had to guess and improve the documentation.

## 5. Independent practice
Create the corresponding artefact in your project repository. Ask another person to review it and record what was unclear or incomplete.

## 6. Knowledge check
1. What is the purpose of this professional practice?
2. What evidence should be preserved?
3. Which risks or constraints need to be disclosed?
4. How will another person verify the work?

## Lesson summary
Professional data science combines sound analysis with ethical judgement, reproducible practice and clear communication.