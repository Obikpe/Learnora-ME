# Lesson 22: Technical Interview Preparation

## Learning outcomes
Apply the professional practice, produce a project artefact and communicate decisions with evidence.

## 1. Core explanation
Technical interviews assess problem-solving, communication and practical judgement. Prepare to explain statistics, SQL, Python, data cleaning, visualisation, model evaluation and project decisions. Practise writing code clearly and explaining time and space complexity where relevant.

For project questions, describe the problem, data, method, validation, result and limitation. Expect follow-ups such as why a metric was selected, how leakage was prevented or what you would change with more time. If you do not know an answer, explain how you would investigate rather than bluffing.

Use timed practice, then review mistakes. Focus on explaining reasoning, not memorising isolated definitions. Prepare questions about the team's data maturity, success criteria, review process and how model outputs are used.

## 2. Worked example or template
Use the example as a starting point and adapt it to your own project. Python examples run in VS Code; shell commands should be entered in the VS Code terminal.

```python
interview_prompts = [
    "Explain the difference between precision and recall.",
    "How would you detect data leakage?",
    "When would you use a median instead of a mean?",
    "Describe a project where you changed your approach.",
    "How would you validate a model on future data?"
]
for q in interview_prompts:
    print("-", q)
```

## 3. Professional application
Keep claims evidence-based. Document sources, assumptions, licences, decisions and limitations. A portfolio project should be understandable and reproducible without access to private data or undocumented local files.

## 4. Guided practice
Answer each prompt aloud in two minutes. For one project, prepare a deeper technical explanation and a plain-language explanation for a non-technical interviewer.

## 5. Independent practice
Create or improve the corresponding project artefact in your repository. Ask another person to review it and record what was unclear or incomplete.

## 6. Knowledge check
1. What is the purpose of this professional practice?
2. What evidence should be preserved?
3. Which risks or constraints need to be disclosed?
4. How will another person verify the work?

## Lesson summary
Professional data science combines sound analysis with ethical judgement, reproducible practice and clear communication.