# Lesson 6: Project Planning and Scoping

## Learning outcomes
Explain the professional practice, apply it to a data-science project and produce evidence that another person can review.

## 1. Core explanation
A project scope defines the problem, deliverables, timeline, dependencies and exclusions. Break work into milestones such as problem framing, data audit, analysis, modelling, validation and communication. Estimate effort and identify risks early: inaccessible data, unclear definitions, small sample size or changing stakeholder needs.

Use a minimum viable deliverable to create early feedback. For example, a data audit and baseline chart may reveal that the original question cannot be answered. This is not failure; it prevents wasted effort. Keep a decision log when scope changes.

Set acceptance criteria for each deliverable. A completed analysis should have reproducible code, documented data, validated results and a report. A project is not complete simply because a notebook has many cells.

## 2. Worked example or template
Use the example as a starting point and adapt it to your own project. Python examples run in VS Code; shell commands should be entered in the VS Code terminal.

```python
milestones = [
    ("Problem and scope", "Approved question and success criteria"),
    ("Data audit", "Source log, data dictionary and quality report"),
    ("Analysis", "Reproducible EDA and findings"),
    ("Model or method", "Baseline and justified candidate"),
    ("Validation", "Error analysis and limitations"),
    ("Delivery", "Report, presentation and repository")
]
for milestone, acceptance in milestones:
    print(milestone, ":", acceptance)
```

## 3. Professional application
Keep claims evidence-based. Document sources, assumptions, licences, decisions and limitations. A portfolio project should be understandable and reproducible without access to private data or undocumented local files.

## 4. Guided practice
Create a two-week project plan with milestones, dependencies, risks and acceptance criteria. Include a contingency if the primary dataset cannot be accessed.

## 5. Independent practice
Create the corresponding artefact in your project repository. Ask another person to review it and record what was unclear or incomplete.

## 6. Knowledge check
1. What is the purpose of this professional practice?
2. What evidence should be preserved?
3. Which risks or constraints need to be disclosed?
4. How will another person verify the work?

## Lesson summary
Professional data science combines sound analysis with ethical judgement, reproducible practice and clear communication.