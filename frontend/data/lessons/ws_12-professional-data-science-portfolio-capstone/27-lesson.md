# Lesson 27: Capstone: Select and Frame the Problem

## Learning outcomes
Apply the professional practice, produce a project artefact and communicate decisions with evidence.

## 1. Core explanation
The capstone begins with a problem that is meaningful, answerable and appropriately scoped. Choose a topic where data can be accessed legally and where you can produce a useful analytical deliverable. Avoid selecting a complex model before understanding the question.

Write a project charter: background, stakeholder, decision, research question, unit of observation, population, time window, target if predictive, success criteria, constraints and risks. Define what is explicitly out of scope. Agree on deliverables and a realistic timeline.

A strong capstone can be descriptive rather than predictive. The project should demonstrate sound reasoning and evidence. If the data cannot answer the question, revise the scope early rather than forcing a model onto unsuitable data.

## 2. Worked example or template
Use the example as a starting point and adapt it to your own project. Python examples run in VS Code; shell commands should be entered in the VS Code terminal.

```python
charter = {
    "title": "Factors associated with late deliveries",
    "decision": "Where should operations investigate service delays?",
    "unit": "Delivery",
    "question": "How do route, dispatch time and distance relate to delay?",
    "deliverable": "EDA report and prioritised recommendations",
    "scope_exclusion": "No causal claims without an intervention design"
}
print(charter)
```

## 3. Professional application
Keep claims evidence-based. Document sources, assumptions, licences, decisions and limitations. A portfolio project should be understandable and reproducible without access to private data or undocumented local files.

## 4. Guided practice
Submit a capstone charter for a project you can complete with available data. Include a clear question, data source plan, success criteria, scope exclusions, ethical review and risks.

## 5. Independent practice
Create or improve the corresponding project artefact in your repository. Ask another person to review it and record what was unclear or incomplete.

## 6. Knowledge check
1. What is the purpose of this professional practice?
2. What evidence should be preserved?
3. Which risks or constraints need to be disclosed?
4. How will another person verify the work?

## Lesson summary
Professional data science combines sound analysis with ethical judgement, reproducible practice and clear communication.