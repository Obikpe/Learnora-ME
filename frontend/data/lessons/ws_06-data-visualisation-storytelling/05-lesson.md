# Lesson 5: Customising and Annotating Charts

## Learning outcomes

By the end of this lesson, you should be able to customise chart size, labels, ticks, grids and legends; add reference lines and annotations; use colour consistently; and make a chart readable without distorting its scale.

## 1. Concepts and reasoning
Customisation should improve interpretation, not merely make a chart elaborate. A useful title states the subject and measure. Axis labels identify variables and units. Tick formatting should match the scale: currency should look like currency, percentages should be labelled as percentages, and dates should be legible.

Annotations add context to a particular value or event. A reference line can show a target, average or threshold. Always label what it represents. A highlighted point should have a reason. Use colour consistently and sparingly; never make the message depend on colour alone.

Be careful with truncated axes. A non-zero baseline can be justified for some line charts, but it can exaggerate small differences in bar charts. If a scale is truncated, make it explicit and explain the choice. Inspect the chart at the size at which the audience will see it.

## 2. Worked example
Run this in VS Code. Install the required libraries if they are not already available: `python -m pip install pandas matplotlib seaborn`.

```python
import matplotlib.pyplot as plt

months = ["Jan", "Feb", "Mar", "Apr", "May"]
completion = [68, 72, 70, 79, 83]
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(months, completion, marker="o")
ax.axhline(80, linestyle="--", label="Target: 80%")
ax.annotate("Target first exceeded", xy=(4, 83), xytext=(2, 86),
            arrowprops={"arrowstyle": "->"})
ax.set(title="Course completion rate", xlabel="Month", ylabel="Completion (%)")
ax.set_ylim(0, 100)
ax.legend()
plt.show()
```

## 3. Interpreting the output
Describe the variables and units shown. Separate what the data visibly demonstrates from your explanation of why it happened. Check whether the axes, ordering, missing values and sample size could change the interpretation. A visual pattern is a clue for further analysis, not a substitute for checking the data.

## 4. Guided practice
Annotate the month with the largest month-to-month increase. Label the target line. Remove the annotation and ask a peer which version communicates the finding more clearly. Record the reason.

## 5. Independent practice
Use a dataset with at least two meaningful variables. Write the analytical question before plotting. Inspect data types and missing values, make a chart, and write a short interpretation with one limitation and one follow-up question.

## 6. Knowledge check
1. Which data types are involved?
2. What question does this chart or technique answer?
3. What would make the result misleading?
4. What additional evidence would strengthen your interpretation?

## Lesson summary
A good visualisation makes the intended comparison easy, labels its scales and units, and does not imply more certainty than the data supports.