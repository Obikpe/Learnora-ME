# Lesson 28: Capstone: Data Acquisition and Preparation

## Learning outcomes
Apply the professional practice, produce a project artefact and communicate decisions with evidence.

## 1. Core explanation
Acquire data according to the charter. Preserve the source version, retrieval date, licence and metadata. Create a data dictionary and verify that the data covers the required population and time window. Do not assume a downloaded file is complete or accurate.

Profile row counts, duplicates, missingness, types, ranges and category values. Define cleaning rules and retain an audit log. Separate raw and processed data. Build a repeatable script or notebook that creates the analytical dataset from the source. Keep personal or restricted data out of public repositories.

If key variables are absent or definitions differ, document the issue and adjust the research question. Do not fabricate missing data or silently replace values. Preparation decisions affect every later conclusion.

## 2. Worked example or template
Use the example as a starting point and adapt it to your own project. Python examples run in VS Code; shell commands should be entered in the VS Code terminal.

```python
import pandas as pd
from pathlib import Path

path = Path("data/raw/source.csv")
df = pd.read_csv(path)
audit = {
    "rows": len(df),
    "columns": len(df.columns),
    "duplicates": int(df.duplicated().sum()),
    "missing_by_column": df.isna().sum().to_dict(),
    "types": df.dtypes.astype(str).to_dict()
}
print(audit)
```

## 3. Professional application
Keep claims evidence-based. Document sources, assumptions, licences, decisions and limitations. A portfolio project should be understandable and reproducible without access to private data or undocumented local files.

## 4. Guided practice
Create a data audit report for your capstone. Include provenance, data dictionary, missingness, duplicates, invalid values and cleaning decisions. State whether the dataset is fit for the charter question.

## 5. Independent practice
Create or improve the corresponding project artefact in your repository. Ask another person to review it and record what was unclear or incomplete.

## 6. Knowledge check
1. What is the purpose of this professional practice?
2. What evidence should be preserved?
3. Which risks or constraints need to be disclosed?
4. How will another person verify the work?

## Lesson summary
Professional data science combines sound analysis with ethical judgement, reproducible practice and clear communication.