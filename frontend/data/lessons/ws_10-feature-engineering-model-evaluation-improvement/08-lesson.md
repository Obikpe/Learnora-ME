# Lesson 8: Feature Selection Fundamentals

## Learning outcomes

By the end of this lesson, you should be able to Explain filter, wrapper and embedded feature selection; fit SelectKBest inside a pipeline; compare selected variables with a baseline; and avoid choosing features using test data.

## 1. Core explanation
Feature selection reduces the input set to variables that contribute useful information for the task. It can improve interpretability, reduce noise, lower training cost and help prevent overfitting. It is not the same as feature extraction: selection keeps original variables, while extraction creates new representations such as PCA components.

Selection must be performed using training data only. If you rank features using the full dataset and then split, information from the test set influences model construction. Use a Pipeline and cross-validation to evaluate selection. The chosen features may change across folds, especially with correlated predictors or small datasets.

A feature with weak individual association may still be useful through interactions. Conversely, a highly associated feature may be redundant or leaked. Combine statistical evidence, domain knowledge, stability and predictive validation.

## 2. Worked Python example
Run in VS Code with the course virtual environment. Install packages with `python -m pip install numpy pandas scikit-learn`.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

data = load_breast_cancer(as_frame=True)
Xtr, Xte, ytr, yte = train_test_split(data.data, data.target,
    test_size=.2, random_state=42, stratify=data.target)
pipe = make_pipeline(SelectKBest(f_classif, k=10),
                     StandardScaler(), LogisticRegression(max_iter=2000))
pipe.fit(Xtr, ytr)
print("Test accuracy:", pipe.score(Xte, yte))
```

## 3. Interpretation and safeguards
State when each feature is available, how it was derived and whether it can be calculated consistently at prediction time. Fit all learned transformations on training data only. Compare performance using the same validation design and check that transformations do not remove meaningful information.

## 4. Guided practice
Change k to 5, 10 and 20 using cross-validation on training data. Explain why selecting features before the split can leak test information.

## 5. Independent practice
Create a small feature-engineering workflow for a dataset. Include a data dictionary, transformation rationale, pipeline and validation plan. Identify one transformation you decided not to use and explain why.

## 6. Knowledge check
1. What information does this transformation add?
2. Could it leak information from after the prediction time?
3. Does it need to be fitted on training data?
4. How will you test its value and stability?

## Lesson summary
Feature engineering should create meaningful, available and reproducible inputs. Every transformation must be justified and validated within a leakage-safe workflow.