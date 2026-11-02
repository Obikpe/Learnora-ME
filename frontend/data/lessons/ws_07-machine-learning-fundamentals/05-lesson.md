# Lesson 5: Mathematics Refresher: Vectors and Matrices

## Learning outcomes
By the end of this lesson, you should be able to explain the key concepts, identify when they apply, implement the worked example in VS Code, and recognise the method's limitations.

## 1. Core explanation
A feature row can be represented as a vector: an ordered list of numbers. If an example has three features, its vector has three coordinates. A dataset with n observations and p features can be represented as an n by p matrix. Rows are observations; columns are features. Keeping this orientation straight prevents many shape errors in Python.

A dot product multiplies corresponding vector elements and adds the results. Linear models use weighted sums of features: prediction = intercept + weight1 × feature1 + ... . A matrix multiplication performs many such weighted sums efficiently. Transpose swaps rows and columns. Shape compatibility matters: multiplying an (n, p) matrix by a (p, 1) weight vector produces an (n, 1) result.

Feature units matter. If one feature is measured in naira and another in years, their numeric scales may differ greatly. Some algorithms are sensitive to scale and require standardisation; tree-based methods are usually less sensitive.

## 2. Worked Python example
Use a project virtual environment. Install relevant packages with `python -m pip install numpy pandas matplotlib scikit-learn scipy` when required.

```python
import numpy as np

# 3 observations, 2 features each
X = np.array([[2, 10], [3, 20], [4, 30]])
weights = np.array([0.5, 0.1])
intercept = 1.0

predictions = X @ weights + intercept
print("X shape:", X.shape)
print("weights shape:", weights.shape)
print("Predictions:", predictions)
```

## 3. Read the result
Do not stop when the code runs. Explain what each input represents, what the output measures and whether the result is plausible. Check data types and shapes. Keep a note of assumptions and information that would not be available at prediction time.

## 4. Guided practice
Write down the shape of a dataset with 120 observations and 5 features. If the model has 5 weights and one intercept, explain why the dot product is valid. Change the number of weights to 4 and inspect the resulting shape error.

## 5. Independent practice
Find or create a small dataset related to the topic. Define its unit of observation and write a data dictionary. Repeat the technique without copying the worked example. Include a brief interpretation and one limitation.

## 6. Knowledge check
1. Define the key terms in this lesson in your own words.
2. When would this method be inappropriate?
3. What can go wrong if data is not representative or is prepared incorrectly?
4. What evidence would you need before trusting the result?

## Lesson summary
Machine learning depends on a clearly defined problem, appropriate data, sound mathematical reasoning and careful evaluation. Tools make implementation easier, but they do not remove the need for judgement.