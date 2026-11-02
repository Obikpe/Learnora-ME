# Lesson 7: Reproducible Project Structure

## Learning outcomes

By the end of this lesson, you should be able to Organise a reproducible data project into raw data, processed data, notebooks, source code, reports and tests; use paths and scripts consistently; and explain why raw data should be preserved.

## 1. Core explanation
A clean project structure separates raw data, processed data, notebooks, reusable source code, reports, tests and configuration. Keep raw data immutable where possible and generate processed data through scripts. Notebooks are useful for exploration, but reusable logic should move into functions or modules.

Use relative paths or a clear project-root strategy rather than hard-coded machine-specific paths. Record dependencies in a requirements file or project metadata. Include a README with setup and run instructions. Do not commit credentials, private datasets or large files without considering repository policy and storage options.

Reproducibility means another person can understand the data source, run the code and obtain consistent outputs. It does not mean results are guaranteed identical across every environment; record package versions and random seeds where relevant.

## 2. Worked example or template
Use the example as a starting point and adapt it to your own project. Python examples run in VS Code; shell commands should be entered in the VS Code terminal.

```python
from pathlib import Path

root = Path("data-science-project")
for folder in ["data/raw", "data/processed", "notebooks", "src",
               "reports/figures", "tests"]:
    (root / folder).mkdir(parents=True, exist_ok=True)
print("Project folders created under:", root.resolve())
```

## 3. Professional application
Keep claims evidence-based. Document sources, assumptions, licences, decisions and limitations. A portfolio project should be understandable and reproducible without access to private data or undocumented local files.

## 4. Guided practice
Create this folder structure for a project. Add a README with setup commands, data provenance, how to run analysis and known limitations. Explain why raw source data should not be overwritten by cleaning scripts.

## 5. Independent practice
Create the corresponding artefact in your project repository. Ask another person to review it and record what was unclear or incomplete.

## 6. Knowledge check
1. What is the purpose of this professional practice?
2. What evidence should be preserved?
3. Which risks or constraints need to be disclosed?
4. How will another person verify the work?

## Lesson summary
Professional data science combines sound analysis with ethical judgement, reproducible practice and clear communication.