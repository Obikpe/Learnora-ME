# Lesson 28: Capstone: Data Acquisition and Preparation

## Learning outcomes
Apply the professional practice, produce the capstone artefact and communicate evidence and limitations clearly.

## 1. Core explanation
Acquire data according to the charter. Preserve the source version, retrieval date, licence and metadata. Create a data dictionary and verify that the data covers the required population and time window. Do not assume a downloaded file is complete or accurate.

Profile row counts, duplicates, missingness, types, ranges and category values. Define cleaning rules and retain an audit log. Separate raw and processed data. Build a repeatable script or notebook that creates the analytical dataset from the source. Keep personal or restricted data out of public repositories.

If key variables are absent or definitions differ, document the issue and adjust the research question. Do not fabricate missing data or silently replace values. Preparation decisions affect every later conclusion.

## 2. Worked example or template
Run the Python example in VS Code where applicable. Adapt paths and fields to your own dataset; do not publish restricted records.

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

## 3. Capstone application
Maintain a decision log and connect every analysis step to the project charter. Preserve provenance and reproducibility. Separate observed results from interpretation and recommendations.

## 4. Guided practice
Create a data audit report for your capstone. Include provenance, data dictionary, missingness, duplicates, invalid values and cleaning decisions. State whether the dataset is fit for the charter question.

## 5. Independent practice
Complete the corresponding capstone deliverable. Ask a reviewer to reproduce or challenge one result and record the changes made in response.

## 6. Knowledge check
1. What evidence does this deliverable provide?
2. Which assumptions or limitations affect the conclusion?
3. How can another person reproduce the work?
4. What is the next responsible action?

## Lesson summary
A capstone demonstrates an end-to-end professional process: a well-framed question, defensible data, reproducible analysis, validation, clear communication and responsible publication.