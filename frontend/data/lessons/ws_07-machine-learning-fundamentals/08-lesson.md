# Lesson 8: Python Tools for Machine Learning

## Learning outcomes
By the end of this lesson, you should be able to explain the key concepts, identify when they apply, implement the worked example in VS Code, and recognise the method's limitations.

## 1. Core explanation
The core Python stack for introductory ML includes NumPy for arrays and numerical operations, pandas for tabular data, Matplotlib and Seaborn for visualisation, and scikit-learn for preprocessing, model training and evaluation. VS Code can run ordinary Python files or notebooks. Use a project-specific virtual environment so dependencies for one project do not interfere with another.

A repeatable environment starts with a folder, virtual environment and requirements file. Activate the environment, install packages and select that interpreter in VS Code. Record package versions when reproducibility matters. Do not install every available library; add only what the project uses.

Scikit-learn follows a consistent estimator interface: fit learns from training data, predict produces outputs, and transform changes data. Many transformers support fit_transform on training data. Crucially, fit preprocessing on training data only; applying fit to the entire dataset before splitting can leak information from the test set.

## 2. Worked Python example
Use a project virtual environment. Install relevant packages with `python -m pip install numpy pandas matplotlib scikit-learn scipy` when required.

```python
# In the VS Code terminal:
# python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
# python -m pip install numpy pandas matplotlib seaborn scikit-learn

import sklearn
import pandas as pd
from sklearn.preprocessing import StandardScaler

print("scikit-learn version:", sklearn.__version__)
sample = pd.DataFrame({"hours": [1, 2, 3, 4]})
scaler = StandardScaler()
print(scaler.fit_transform(sample))
```

## 3. Read the result
Do not stop when the code runs. Explain what each input represents, what the output measures and whether the result is plausible. Check data types and shapes. Keep a note of assumptions and information that would not be available at prediction time.

## 4. Guided practice
Create a fresh VS Code folder and virtual environment. Install only pandas, NumPy, Matplotlib and scikit-learn. Save package versions with pip freeze. Explain why selecting the correct interpreter matters when code works in one terminal but not another.

## 5. Independent practice
Find or create a small dataset related to the topic. Define its unit of observation and write a data dictionary. Repeat the technique without copying the worked example. Include a brief interpretation and one limitation.

## 6. Knowledge check
1. Define the key terms in this lesson in your own words.
2. When would this method be inappropriate?
3. What can go wrong if data is not representative or is prepared incorrectly?
4. What evidence would you need before trusting the result?

## Lesson summary
Machine learning depends on a clearly defined problem, appropriate data, sound mathematical reasoning and careful evaluation. Tools make implementation easier, but they do not remove the need for judgement.