# Lesson 1: The Professional Data Scientist's Role

## Learning outcomes

By the end of this lesson, you should be able to Describe the responsibilities of a professional data scientist across problem framing, data work, analysis, modelling, communication and governance; and distinguish evidence-based practice from simply applying tools.

## 1. Core explanation
A data scientist turns data into evidence that supports decisions. The work includes problem framing, data acquisition, analysis, modelling, evaluation, communication and responsible use. The role is collaborative: domain experts explain the context, engineers support reliable systems, analysts understand reporting needs and decision-makers own the actions.

Not every problem needs machine learning. Descriptive analysis may explain what happened; diagnostic analysis explores why; predictive analysis estimates what may happen; prescriptive analysis compares possible actions. Choose the least complex method that answers the question well. A sophisticated model without a decision context is not valuable work.

Professional practice includes documenting assumptions, protecting data, communicating uncertainty and being willing to say that the evidence is insufficient. A data scientist is accountable not only for code but for the interpretation and consequences of the work.

## 2. Worked example or template
Use the example as a starting point and adapt it to your own project. Python examples run in VS Code; shell commands should be entered in the VS Code terminal.

```python
role_map = {
    "Problem framing": "Define the decision and success criteria",
    "Data work": "Acquire, validate and prepare relevant data",
    "Analysis": "Explore patterns and test explanations",
    "Modelling": "Build only where prediction adds value",
    "Communication": "Explain evidence, uncertainty and limitations",
    "Governance": "Protect data and monitor consequences"
}
for stage, purpose in role_map.items():
    print(stage, "->", purpose)
```

## 3. Professional application
Keep claims evidence-based. Document sources, assumptions, licences, decisions and limitations. A portfolio project should be understandable and reproducible without access to private data or undocumented local files.

## 4. Guided practice
Choose a business problem and identify which parts require a data scientist, domain expert, data engineer and decision owner. Explain why these responsibilities should not all be silently assigned to the model developer.

## 5. Independent practice
Create the corresponding artefact in your project repository. Ask another person to review it and record what was unclear or incomplete.

## 6. Knowledge check
1. What is the purpose of this professional practice?
2. What evidence should be preserved?
3. Which risks or constraints need to be disclosed?
4. How will another person verify the work?

## Lesson summary
Professional data science combines sound analysis with ethical judgement, reproducible practice and clear communication.