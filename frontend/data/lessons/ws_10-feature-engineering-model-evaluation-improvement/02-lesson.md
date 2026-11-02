# Lesson 2: Data Leakage and Leakage Prevention

## Learning outcomes
Explain the feature-engineering method, implement it in Python and identify leakage, reproducibility and interpretation risks.

## 1. Core explanation
Data leakage occurs when training or evaluation uses information that would not legitimately be available at prediction time, or when information from validation/test data influences training. Target leakage includes a post-outcome field that directly or indirectly reveals the answer. Preprocessing leakage occurs when statistics such as medians or scaling parameters are learned using the full dataset before splitting.

Leakage creates an overly optimistic estimate and often causes deployment failure. Examples include using a discharge code to predict hospital mortality before discharge, or calculating a customer feature using transactions after the prediction date. Duplicate or related records across partitions can also leak identity-specific information.

Prevent leakage by defining the prediction timestamp, using time-aware or group-aware splits, fitting transformations inside Pipelines and keeping the final test set untouched. Review feature lineage, not only column names. A feature can be suspicious even when it has no obvious target-like name.

## 2. Worked Python example
Run in VS Code with the course virtual environment. Install packages with `python -m pip install numpy pandas scikit-learn`.

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression

df = pd.DataFrame({"x": [1, 2, None, 4, 5, None, 7, 8],
                   "y": [0, 0, 0, 0, 1, 1, 1, 1]})
Xtr, Xte, ytr, yte = train_test_split(df[["x"]], df["y"],
                                      test_size=.25, random_state=1)
pipe = make_pipeline(SimpleImputer(strategy="median"), LogisticRegression())
pipe.fit(Xtr, ytr)
print("Test score:", pipe.score(Xte, yte))
```

## 3. Interpretation and safeguards
State when each feature is available, how it was derived and whether it can be calculated consistently at prediction time. Fit all learned transformations on training data only. Compare performance using the same validation design and check that transformations do not remove meaningful information.

## 4. Guided practice
Describe a scenario where a feature is recorded after the target outcome. Explain why high test accuracy from that feature is invalid. Then explain why the Pipeline prevents the imputer from learning its median from test rows.

## 5. Independent practice
Create a small feature-engineering workflow for a dataset. Include a data dictionary, transformation rationale, pipeline and validation plan. Identify one transformation you decided not to use and explain why.

## 6. Knowledge check
1. What information does this transformation add?
2. Could it leak information from after the prediction time?
3. Does it need to be fitted on training data?
4. How will you test its value and stability?

## Lesson summary
Feature engineering should create meaningful, available and reproducible inputs. Every transformation must be justified and validated within a leakage-safe workflow.