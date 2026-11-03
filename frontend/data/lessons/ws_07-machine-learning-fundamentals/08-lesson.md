# Lesson 8: Python Tools for Machine Learning

## Learning outcomes
Set up a project-specific Python environment in VS Code; install and import the core ML libraries; understand arrays and DataFrames; use scikit-learn estimators and transformers; and build a simple pipeline.

![Python machine-learning toolkit](/course-assets/ws07/08-python-ml-toolkit.svg)

## 1. The core Python toolkit
- **Python:** programming language used to organise the workflow.
- **NumPy:** efficient numerical arrays and mathematical operations.
- **Pandas:** labelled tabular data through Series and DataFrame.
- **Matplotlib / Seaborn:** charts for data inspection and communication.
- **SciPy:** scientific and statistical functions.
- **scikit-learn:** preprocessing, classical ML algorithms, model selection and evaluation.
- **Jupyter:** interactive notebooks, useful for exploration and explanation.

These libraries have different roles. Pandas helps inspect a table; NumPy performs numerical operations; scikit-learn provides consistent interfaces for learning and preprocessing.

## 2. Create a clean project in VS Code
Create a folder, open it in VS Code and open the integrated terminal.

```bash
python --version
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

If PowerShell blocks activation, follow your organisation's device policy rather than changing security settings blindly. You can also call the environment's Python executable directly.

Install the course packages:
```bash
python -m pip install --upgrade pip
python -m pip install numpy pandas matplotlib seaborn scikit-learn scipy jupyter
```

In VS Code, choose the interpreter inside .venv using the Python interpreter selector. A frequent beginner problem is installing a library in one Python environment and running the script with another.

## 3. Imports and aliases
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn
```
The names np, pd, plt and sns are conventional aliases. They are shorter names used in code. The aliases do not change the libraries. Import only what you need, and avoid naming your own files numpy.py, pandas.py or sklearn.py because that can shadow the real package.

## 4. NumPy arrays and Pandas tables
```python
import numpy as np
import pandas as pd

values = np.array([[1, 2], [3, 4], [5, 6]])
print(values.shape, values.mean())

df = pd.DataFrame({
    "hours": [2, 4, 6],
    "attendance": [70, 85, 95]
})
print(df.head())
print(df.dtypes)
print(df.describe())
```
NumPy arrays are useful for numerical computation. Pandas DataFrames add column labels and flexible data types. A Series is one labelled column; a DataFrame is a two-dimensional table.

## 5. The scikit-learn estimator pattern
Most scikit-learn models follow a consistent interface:
- `fit(X, y)`: learn parameters from features X and target y.
- `predict(X)`: return predicted labels or values.
- `predict_proba(X)`: return class probability estimates for estimators that support it.
- `transform(X)`: transform features, for example by scaling.
- `fit_transform(X)`: learn a transformation and apply it, commonly on training data.
- `score(X, y)`: estimator-specific score; check what it means for that estimator.

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

data = load_iris(as_frame=True)
X, y = data.data, data.target
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
model = DecisionTreeClassifier(max_depth=3, random_state=42)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
print("Accuracy:", model.score(X_test, y_test))
```

The Iris dataset is a small educational dataset. The model learns from the training portion and is scored on held-out rows. The random seed makes this split repeatable in the same environment.

## 6. Why pipelines matter
A pipeline chains transformations and a final estimator. During fitting, each transformation is learned from training data, then applied in sequence. This reduces the chance of accidentally fitting a scaler or imputer on test data.

```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

pipeline = make_pipeline(
    StandardScaler(),
    LogisticRegression(max_iter=1000)
)
pipeline.fit(X_train, y_train)
print("Pipeline accuracy:", pipeline.score(X_test, y_test))
```

StandardScaler learns each feature's mean and standard deviation during fit, then transforms values into standardised units. Logistic regression uses those scaled values. The pipeline ensures that the test data is transformed using training-set statistics rather than recalculating them from the test set.

## 7. Package versions and requirements
Check versions:
```bash
python -m pip show numpy pandas scikit-learn
python -m pip freeze > requirements.txt
```
A requirements file records installed package versions. It helps recreate an environment, although exact reproducibility may also depend on Python version, operating system and hardware.

## 8. Common errors
- Wrong interpreter selected in VS Code.
- Installing packages with a different Python executable.
- Naming a local file after a library.
- Forgetting parentheses on functions such as fit().
- Passing a one-dimensional target where a two-dimensional feature matrix is expected, or vice versa.
- Preprocessing the full dataset before splitting.

## Guided practice
Create a virtual environment, install the packages and run the Iris example. Print the shapes of X_train, X_test, y_train and y_test. Explain why X has two dimensions but y normally has one.

## Independent practice
Create a small project folder with main.py, data/, requirements.txt and README.md. Load a CSV using Pandas, inspect it, split X and y, and fit a simple scikit-learn model. Record the Python and package versions.

## Knowledge check
1. What is the role of NumPy compared with Pandas?
2. What does fit() do?
3. What does transform() do?
4. Why is a pipeline useful?
5. Why might a package import fail even after installation?

## Lesson summary
A reliable Python environment and familiarity with the fit/transform/predict pattern make ML experiments repeatable. Tool fluency supports good reasoning; it does not replace it.