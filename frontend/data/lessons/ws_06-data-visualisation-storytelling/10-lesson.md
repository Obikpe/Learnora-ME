# Lesson 10: Time-Series Visualisation

## Why this lesson matters

This lesson is part of **ws_06 data visualisation storytelling**. It builds on earlier work and prepares you for the next stage. The goal is not to memorise commands: it is to understand the problem, choose an appropriate method, implement it in Python, inspect the result and explain what the result does and does not establish.

## Learning outcomes

By the end, you should be able to:
- Explain the central idea and the problem this method addresses.
- Identify the data, assumptions and conditions needed to use it.
- Implement a basic version in Python and explain the important lines.
- Interpret the output, recognise common failure modes and communicate limitations.
- Apply the method to a small realistic data-science question.

## 1. Start with the problem

Before choosing a technique, state the question in plain language. Identify the unit being analysed (a person, transaction, product, day or observation), the outcome or quantity of interest, the available variables and the decision the analysis should support. This prevents a common mistake: selecting a familiar algorithm or chart first and then trying to invent a question for it.

Write down what one row represents. Check whether rows are independent, whether identifiers are duplicated, whether values are missing and whether the time period is appropriate. A method cannot repair a poorly defined question or an unsuitable dataset.

## 2. Understand the concept

**Time-Series Visualisation** should be understood as a tool within a wider analytical workflow. Learn its purpose, the assumptions behind it, the kind of input it expects and the form of output it produces. Distinguish what the method calculates from the interpretation an analyst makes. A numerical result is evidence to investigate, not automatically a conclusion.

For a first attempt, use a small dataset that can be inspected manually. Predict what you expect to happen before running the code. Then compare the actual output with that expectation. This habit makes debugging and interpretation much easier.

## 3. A Python starting point

The following is a teaching pattern. It assumes that a DataFrame named `data` has already been loaded and that the named columns exist. Adapt the columns to your dataset rather than copying names blindly.

```python
import matplotlib.pyplot as plt

months = ["Jan", "Feb", "Mar", "Apr"]
revenue = [12, 15, 13, 19]
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(months, revenue, marker="o")
ax.set(title="Monthly revenue", xlabel="Month", ylabel="Revenue (₦m)")
ax.grid(alpha=0.25)
plt.tight_layout()
plt.show()
```

Read the code from top to bottom. Identify the input variables, the operation being performed and the output. Check dimensions and data types before fitting a model or producing a chart. Fix warnings and errors at their source rather than suppressing them.

## 4. Work through the result

Ask four questions:
1. What exactly did the code calculate or produce?
2. Which rows and columns contributed to the result?
3. Which assumptions would make the result misleading?
4. What independent check could confirm that the result is plausible?

Compare a small sample with a manual calculation or a simple baseline. If the output is unexpected, inspect the data first, then the parameters and finally the method. Do not keep changing settings until a preferred result appears.

## 5. Common mistakes

- Applying a technique before defining the analytical question.
- Ignoring missing values, unusual observations or duplicate records.
- Using variables that would not be available at the time a real prediction or decision is made.
- Treating a metric, chart or model output as proof of causation.
- Failing to record the dataset, parameters, random seed and software versions.
- Reporting a result without explaining its uncertainty and limitations.

## Guided practice

1. Explain the lesson's central concept in your own words.
2. Identify a suitable small dataset and describe its row-level unit.
3. Run the example after checking that the required columns exist.
4. Change one input or setting and describe how the output changes.
5. Inspect at least five observations and verify that the output is plausible.
6. Write down one limitation and one additional check you would perform.

## Independent practice

Choose a small, relevant dataset and formulate one clear question that this lesson's method can help answer. Create a reproducible Python script, document the input columns and preprocessing, run the method, inspect the output and write a short interpretation. Include the assumptions, one alternative explanation and a limitation. Your work should be understandable to another learner who has not watched you run it.

## Summary

The key skill is to connect the analytical question, the data, the method and the interpretation. Understand the assumptions, make the workflow reproducible, inspect outputs and communicate limitations. The next lesson extends this idea to a more demanding problem.

## Further reflection

What would change if the dataset were ten times larger, contained more missing values or came from a different population? Which parts of your workflow would remain valid, and which would need to be reconsidered?
