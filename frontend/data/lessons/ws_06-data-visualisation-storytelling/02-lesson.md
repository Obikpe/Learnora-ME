# Lesson 2: Understanding Data Types and Visual Variables

## Learning outcomes
By the end of this lesson, you should be able to explain the central ideas, select an appropriate method, implement it in Python, interpret the output and identify limitations.

## 1. Concepts and reasoning
Chart choice begins with the meaning of each field. Numerical data may be continuous (temperature, duration) or discrete counts (number of visits). Categorical data describes groups such as department or product. Ordinal categories have a meaningful order (low, medium, high); nominal categories do not. Dates and times are ordered values and need temporal handling.

Visual variables include position, length, angle, area, colour hue, lightness, shape and line style. Position and length support accurate comparisons. Hue distinguishes a few categories but does not imply magnitude. Sequential lightness is suitable for ordered values; a diverging palette is suitable when values have a meaningful midpoint such as zero or a target.

Category codes are not measurements. If departments are encoded as 1, 2 and 3, a line joining those codes suggests order and distance that do not exist. Convert them to labels and use a categorical chart. Similarly, a rainbow palette is poor for ordered values because colour changes do not communicate a reliable numerical progression.

## 2. Worked example
Run this in VS Code. Install the required libraries if they are not already available: `python -m pip install pandas matplotlib seaborn`.

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.DataFrame({
    "department": ["Sales", "Support", "Engineering"],
    "tickets": [120, 95, 70]
})
fig, ax = plt.subplots()
ax.bar(df["department"], df["tickets"])
ax.set_xlabel("Department")
ax.set_ylabel("Tickets handled")
ax.set_title("Tickets handled by department")
plt.show()
```

## 3. Interpreting the output
Describe the variables and units shown. Separate what the data visibly demonstrates from your explanation of why it happened. Check whether the axes, ordering, missing values and sample size could change the interpretation. A visual pattern is a clue for further analysis, not a substitute for checking the data.

## 4. Guided practice
Classify learner level (beginner/intermediate/advanced), course name, score and completion date as nominal, ordinal, continuous, discrete or temporal. Choose a visual variable for each. Explain why assigning course names the numbers 1, 2 and 3 would be misleading.

## 5. Independent practice
Use a dataset with at least two meaningful variables. Write the analytical question before plotting. Inspect data types and missing values, make a chart, and write a short interpretation with one limitation and one follow-up question.

## 6. Knowledge check
1. Which data types are involved?
2. What question does this chart or technique answer?
3. What would make the result misleading?
4. What additional evidence would strengthen your interpretation?

## Lesson summary
A good visualisation makes the intended comparison easy, labels its scales and units, and does not imply more certainty than the data supports.