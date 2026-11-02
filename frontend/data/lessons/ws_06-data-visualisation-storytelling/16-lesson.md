# Lesson 16: Data Storytelling and Narrative Structure

## Learning outcomes

By the end of this lesson, you should be able to structure a data narrative using context, question, evidence, insight and action; distinguish observation from interpretation; select supporting visuals; and communicate caveats without cherry-picking.

## 1. Core explanation
Data storytelling connects evidence to a decision through a clear narrative. A useful structure is context, complication, evidence, insight and action. Context explains the situation; complication identifies the question or tension; evidence supports the insight; action states what can reasonably be done.

A story is not permission to cherry-pick. Show the relevant population, time window and denominator. Include counter-evidence and uncertainty. A chart should support one message, with annotation that guides attention but does not distort the data. Separate observed facts from interpretations and recommendations.

Tailor detail to the audience. Executives need the decision and implications; technical audiences may need methods, assumptions and diagnostics. Keep a technical appendix available so the main narrative remains focused without hiding important information.

## 2. Worked Python example
Run in VS Code. Install required packages with `python -m pip install pandas numpy matplotlib seaborn plotly`.

```python
story = [
    "Context: learner completion is a priority",
    "Complication: two cohorts show a declining rate",
    "Evidence: completion fell from 82% to 74% over six weeks",
    "Insight: the decline is concentrated in the two cohorts",
    "Action: investigate support access; do not assume causation"
]
print("\n".join(story))
```

## 3. Interpretation and design checks
State the analytical question, population, variables, units and denominator. Check missingness and sample size. Distinguish observations from explanations and recommendations. Design for the actual audience and the size at which the visual will be viewed.

## 4. Guided practice
Write a five-sentence narrative for a chart you created. Include context, a specific finding, a limitation and a proportionate action. Identify one alternative explanation.

## 5. Independent practice
Apply the lesson to a dataset. Create a chart or artefact, write a caption that states the main message and caveat, and ask another person to interpret it without your explanation.

## 6. Knowledge check
1. What question does this visual answer?
2. Which encoding or design choice supports the comparison?
3. What could mislead the audience?
4. What uncertainty or limitation must be disclosed?

## Lesson summary
Effective visual communication combines accurate encoding, clear context, audience-aware design and honest interpretation.