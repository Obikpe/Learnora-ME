# Lesson 27: Capstone: Select and Frame the Problem

## Learning outcomes
Apply the professional practice, produce the capstone artefact and communicate evidence and limitations clearly.

## 1. Core explanation
The capstone begins with a problem that is meaningful, answerable and appropriately scoped. Choose a topic where data can be accessed legally and where you can produce a useful analytical deliverable. Avoid selecting a complex model before understanding the question.

Write a project charter: background, stakeholder, decision, research question, unit of observation, population, time window, target if predictive, success criteria, constraints and risks. Define what is explicitly out of scope. Agree on deliverables and a realistic timeline.

A strong capstone can be descriptive rather than predictive. The project should demonstrate sound reasoning and evidence. If the data cannot answer the question, revise the scope early rather than forcing a model onto unsuitable data.

## 2. Worked example or template
Run the Python example in VS Code where applicable. Adapt paths and fields to your own dataset; do not publish restricted records.

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

## 3. Capstone application
Maintain a decision log and connect every analysis step to the project charter. Preserve provenance and reproducibility. Separate observed results from interpretation and recommendations.

## 4. Guided practice
Submit a capstone charter for a project you can complete with available data. Include a clear question, data source plan, success criteria, scope exclusions, ethical review and risks.

## 5. Independent practice
Complete the corresponding capstone deliverable. Ask a reviewer to reproduce or challenge one result and record the changes made in response.

## 6. Knowledge check
1. What evidence does this deliverable provide?
2. Which assumptions or limitations affect the conclusion?
3. How can another person reproduce the work?
4. What is the next responsible action?

## Lesson summary
A capstone demonstrates an end-to-end professional process: a well-framed question, defensible data, reproducible analysis, validation, clear communication and responsible publication.