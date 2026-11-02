# Lesson 17: Presenting Insights to Different Audiences

## Learning outcomes

By the end of this lesson, you should be able to adapt one analytical finding for executive, technical and operational audiences; preserve the same evidence and caveats; choose an appropriate level of detail; and respond clearly to questions about uncertainty.

## 1. Core explanation
The same analysis needs different explanations for different audiences. A decision-maker needs the question, finding, implication, risk and recommended action. A technical reviewer needs data definitions, sampling, methods, assumptions, diagnostics and reproducibility. An operational user needs to know what to do, when to do it and when not to trust the output.

Do not change the underlying evidence when changing the presentation. Change the level of detail and vocabulary. Define terms rather than assuming shared knowledge. Use annotations to guide attention, but leave enough context for the reader to verify the claim. Be prepared to explain uncertainty and answer “what would change your recommendation?”

A good presentation distinguishes three layers: what was observed, what it may mean and what action is justified. Keep the technical appendix available and disclose limitations in the main narrative when they affect the decision.

## 2. Worked Python example
Run in VS Code. Install required packages with `python -m pip install pandas numpy matplotlib seaborn plotly`.

```python
audience_messages = {
    "executive": "Completion declined by 8 percentage points; investigate support access in two cohorts.",
    "technical": "The six-week cohort comparison is descriptive; sample sizes and confounding limit causal inference.",
    "operations": "Review support requests and attendance for the two cohorts before changing the programme."
}
for audience, message in audience_messages.items():
    print(audience.title(), ":", message)
```

## 3. Interpretation and design checks
State the analytical question, population, variables, units and denominator. Check missingness and sample size. Distinguish observations from explanations and recommendations. Design for the actual audience and the size at which the visual will be viewed.

## 4. Guided practice
Take one finding and write three versions: executive, technical and operational. Check that the evidence and caveat remain consistent across all three.

## 5. Independent practice
Apply the lesson to a dataset. Create a chart or artefact, write a caption that states the main message and caveat, and ask another person to interpret it without your explanation.

## 6. Knowledge check
1. What question does this visual answer?
2. Which encoding or design choice supports the comparison?
3. What could mislead the audience?
4. What uncertainty or limitation must be disclosed?

## Lesson summary
Effective visual communication combines accurate encoding, clear context, audience-aware design and honest interpretation.