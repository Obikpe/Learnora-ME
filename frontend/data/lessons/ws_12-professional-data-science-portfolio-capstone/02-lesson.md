# Lesson 2: Turning a Vague Request into an Analytical Problem

## Learning outcomes
Explain the professional practice, apply it to a data-science project and produce evidence that another person can review.

## 1. Core explanation
Stakeholder requests often begin as symptoms: “sales are falling”, “find risky learners” or “show which customers matter”. Convert the request into a specific decision and measurable question. Ask who needs the answer, what action they can take, when it is needed and what would count as success.

Separate the problem from a proposed solution. “Build a dashboard” is a solution; “identify which regions have declining retention early enough to intervene” is a problem. Define the unit of analysis, time window, population and constraints. Identify what evidence is needed and what is outside scope.

Use a problem statement that can be falsified or evaluated. Avoid vague success criteria such as “improve performance”. Define a baseline, target metric and guardrails so that improvement in one measure does not create unacceptable harm elsewhere.

## 2. Worked example or template
Use the example as a starting point and adapt it to your own project. Python examples run in VS Code; shell commands should be entered in the VS Code terminal.

```python
problem = {
    "request": "Improve learner completion",
    "decision": "Which cohorts need additional support next week?",
    "unit": "Learner-week",
    "population": "Active learners in current cohorts",
    "success": "Earlier identification with manageable false-alert rate",
    "guardrail": "No automatic penalties based on a risk score"
}
print(problem)
```

## 3. Professional application
Keep claims evidence-based. Document sources, assumptions, licences, decisions and limitations. A portfolio project should be understandable and reproducible without access to private data or undocumented local files.

## 4. Guided practice
Rewrite “we need AI to increase sales” into a measurable analytical problem. State the stakeholder, decision, unit, time horizon, baseline and success measure.

## 5. Independent practice
Create the corresponding artefact in your project repository. Ask another person to review it and record what was unclear or incomplete.

## 6. Knowledge check
1. What is the purpose of this professional practice?
2. What evidence should be preserved?
3. Which risks or constraints need to be disclosed?
4. How will another person verify the work?

## Lesson summary
Professional data science combines sound analysis with ethical judgement, reproducible practice and clear communication.