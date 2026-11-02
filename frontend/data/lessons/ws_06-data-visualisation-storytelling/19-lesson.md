# Lesson 19: Visual Storytelling, Accessibility and Audience Communication

## Learning outcomes
You should be able to structure a visual narrative; write message-led titles and captions; use annotations responsibly; choose accessible colour and typography; communicate uncertainty and limitations; cite data sources; and adapt a visual for different audiences without changing the evidence.

## 1. What is data storytelling?
Data storytelling connects evidence to a question and a decision. It is not making a chart dramatic or selecting only numbers that support a preferred conclusion.

A clear narrative often contains:
1. **Context:** what situation are we examining?
2. **Question:** what do we need to understand?
3. **Evidence:** what does the data show?
4. **Interpretation:** what might the pattern mean?
5. **Action:** what can reasonably be done next?

A strong story distinguishes what was observed, what is inferred and what is recommended.

## 2. Message-led titles
A generic title says “Monthly revenue”. A message-led title might say “Revenue increased in four of six months but remained below target”. The title should communicate a defensible finding, not exaggerate it.

A subtitle can explain population and period. A caption can state unit, source, denominator and caveat.

Example:
- Title: “Completion improved from January to June”.
- Subtitle: “Six monthly observations across two training cohorts”.
- Caption: “Completion is learners completing divided by learners enrolled. Cohort sizes changed during the period, so the chart is descriptive and does not establish why completion changed.”

## 3. Annotate only what matters
Annotations can identify a target, policy date, unusual observation, threshold crossing or meaningful change. They should add context. Do not label every point. Do not write a causal statement next to a line unless the research design supports causality.

## 4. Colour and accessibility
Use qualitative palettes for unrelated categories, sequential palettes for low-to-high values and diverging palettes for values around a meaningful midpoint. Do not rely on colour alone: add labels, marker shapes, line styles or patterns. Ensure text contrast and font sizes are readable. Check whether the chart remains understandable in grayscale and for people with colour-vision differences.

Seaborn includes palettes such as `"colorblind"`; Matplotlib supports many colour maps. A palette is not automatically accessible simply because it looks attractive.

## 5. Show context and uncertainty
A percentage needs a denominator. A count needs a population or exposure context. A trend needs a time window. A mean may need spread or uncertainty.

Suppose one region has 100 complaints and another has 50. If the first serves 10,000 customers and the second serves 1,000, complaint rates are 10 and 50 per 1,000 customers. Counts and rates answer different questions.

## 6. Build a message-led chart
```python
import matplotlib.pyplot as plt

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
completion = [68, 70, 69, 74, 78, 80]
target = 75

fig, ax = plt.subplots(figsize=(9, 5), layout="constrained")
ax.plot(months, completion, marker="o", linewidth=2.5,
        color="#2457A7", label="Completion rate")
ax.axhline(target, linestyle="--", color="#B23A48",
           label="Target: 75%")
ax.set_title("Completion reached the 75% target in May",
             loc="left", fontsize=15)
ax.set_xlabel("Month")
ax.set_ylabel("Completion rate (%)")
ax.set_ylim(0, 100)
ax.legend(frameon=False)
ax.annotate("First month above target",
            xy=("May", 78), xytext=("Mar", 90),
            arrowprops={"arrowstyle": "->"})
fig.text(0.01, -0.02,
         "Illustrative data. Completion = learners completing / learners enrolled.",
         fontsize=8)
plt.show()
```

The title states the message. The axis includes the unit. The target is explicit. The note defines the denominator. Because the values are illustrative, the note avoids pretending they are a real programme result.

## 7. Adapt to the audience
- **Executive:** finding, decision implication, risk and recommendation.
- **Technical reviewer:** data definitions, sampling, methods, assumptions, diagnostics and reproducibility.
- **Operational team:** action, threshold and when to escalate.
- **General audience:** plain language, clear labels, limited jargon and sufficient context.

Never remove an important caveat because the audience is non-technical. Explain it in simpler language.

## 8. Source notes and reproducibility
Record the dataset name and source, licence, retrieval date, population and period, cleaning rules, metric definitions and denominator, and Python packages or script used. A chart image without its method is difficult to audit. Save code and a README alongside outputs.

## 9. Common storytelling mistakes
- Cherry-picking a time period.
- Truncating an axis to exaggerate a difference.
- Writing a causal title from descriptive evidence.
- Omitting sample sizes or denominators.
- Using colour without a legend.
- Hiding missingness or uncertainty.
- Showing a chart without explaining the decision it supports.

## Guided practice
1. Rewrite a generic title as a message-led title.
2. Add a denominator note.
3. Add one meaningful annotation.
4. Check palette accessibility.
5. Write executive and technical versions of the same finding without changing the evidence.

## Independent practice
Choose a chart from an earlier lesson. Improve its title, labels, units, source note and caveat. Prepare an explanation for a decision-maker and a technical reviewer. Confirm both versions state the same evidence and limitations.

## Knowledge check
1. What are the five parts of a useful data narrative?
2. What makes a title message-led?
3. Why is a denominator important?
4. Why should colour not be the only encoding?
5. How can the same evidence be communicated differently without changing the truth?

## Lesson summary
A visual story is an evidence-based explanation, not decoration or persuasion at any cost. Use message-led titles, clear denominators, accessible colour, useful annotations and honest caveats. Adapt detail to the audience while preserving the evidence.