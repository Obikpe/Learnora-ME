# Lesson 17: From Analysis to a Clear Data Story

## Why this lesson matters
A chart is not automatically a story. A data story connects a decision-maker's question to relevant evidence, explains what the evidence means and makes the next step clear. The goal is not to decorate a report; it is to help an audience understand a finding without overstating what the data proves.

## Learning outcomes
You will define an audience and decision, organise evidence into a narrative, select a small sequence of purposeful Python charts, write useful titles and annotations, and distinguish findings from hypotheses and recommendations.

## 1. Start with the decision
Before opening Matplotlib, answer:
- Who will use this analysis?
- What decision are they trying to make?
- What do they already know?
- What evidence would change their decision?
- What can the available data not tell us?

A chart about monthly revenue may be useful to a sales manager deciding where to investigate. It may be irrelevant to a customer-support manager unless the data connects revenue to support activity.

## 2. Build the narrative spine
A practical structure is:
1. **Context:** what is being examined and why?
2. **Question:** what needs to be understood?
3. **Evidence:** what do the data and comparisons show?
4. **Interpretation:** what might explain the pattern?
5. **Action:** what should happen next, and how will it be evaluated?

Do not force every analysis into a dramatic rise-and-fall story. Sometimes the most useful result is that there is no meaningful difference or that the data is insufficient.

## 3. Choose a small chart sequence
Use each visual to answer a distinct question. For a retail performance story:
- a line chart establishes the monthly trend;
- a ranked bar chart compares categories;
- a scatterplot explores the relationship between discount and order value;
- a distribution plot shows variation hidden by the average.

Avoid repeating the same metric in several chart types merely to make the report look longer.

## 4. Create a question-led chart in Python
```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(monthly["month"], monthly["revenue"], marker="o")
ax.set_title("Monthly revenue across the reporting period")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue")
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
plt.show()
```
The title states what is being measured and the time context should be clear in the accompanying text. Add currency units to the axis label where appropriate. Avoid decorative effects that compete with the data.

## 5. Write a useful chart caption
A good caption does more than repeat the title. It can state:
- the key pattern;
- the comparison or period that makes it meaningful;
- an important caveat.

For example: “Revenue increased in the final quarter, but the dataset does not include marketing spend or product availability, so the chart cannot identify the cause.”

## 6. Annotate with restraint
Annotations should direct attention to a meaningful event, threshold or comparison. They should not imply causation. If a date marks a policy change, label it as a policy change; do not label it as the cause of a revenue shift unless the analysis supports that claim.

## 7. Separate evidence from interpretation
Use explicit language:
- Evidence: “The median order value was higher in group A than group B.”
- Interpretation: “This may indicate different purchasing patterns.”
- Hypothesis: “The difference may relate to customer mix.”
- Recommendation: “Investigate the product mix before changing pricing.”

The distinction protects the audience from treating an explanation as a proven fact.

## 8. Structure the final communication
A concise analytical story can use:
- a headline finding;
- one paragraph of context and scope;
- two to five charts in a deliberate order;
- a short interpretation under each chart;
- recommendations and limitations.

Keep technical details such as missing-value rules, data definitions and model assumptions in a methods section or appendix, but make them accessible.

## Common mistakes
- Starting with a chart before clarifying the decision.
- Showing too many visuals with no narrative connection.
- Writing causal headlines from descriptive evidence.
- Hiding uncertainty, sample size or missing data.
- Using captions that merely repeat axis labels.
- Ending with a recommendation unsupported by the analysis.

## Guided practice
Use the monthly revenue and category summaries from WS05. Write a one-sentence decision question, create a trend chart and a category ranking, then write one evidence statement, one possible explanation and one action for further investigation.

## Independent assignment
Prepare a two-page Python-generated data story for a non-technical audience. Include three to five charts, a clear headline, captions, one recommendation, data definitions and limitations. A reviewer should understand the main conclusion without reading the code.

## Self-check
What decision is the audience making? What is the difference between evidence and interpretation? Why should a chart title communicate the question? When does an annotation become misleading? How can a story communicate that the data is insufficient?

## Lesson takeaway
A data story is a structured argument built from evidence. Visuals support the reasoning; they do not replace it.
