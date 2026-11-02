# Lesson 4: Finding and Assessing Data Sources

## Learning outcomes

By the end of this lesson, you should be able to Find potential data sources; assess ownership, provenance, coverage, freshness, definitions and licence; and document why a source is or is not fit for the project question.

## 1. Core explanation
Data may come from internal databases, public portals, APIs, surveys, sensors or licensed providers. Assess relevance, coverage, collection method, update frequency, missingness, definitions, provenance and permitted use. A large dataset is not automatically representative or accurate.

Check whether the data matches the population and time period of the question. A national dataset may not describe one city; a survey of volunteers may not represent all residents. Inspect metadata and data dictionaries, and verify that units and category definitions are consistent.

Keep a source log with owner, URL or access method, retrieval date, licence, version and known limitations. Do not scrape or redistribute data without checking the terms. If a source cannot be verified, disclose that uncertainty rather than presenting it as authoritative.

## 2. Worked example or template
Use the example as a starting point and adapt it to your own project. Python examples run in VS Code; shell commands should be entered in the VS Code terminal.

```python
source_record = {
    "name": "Example public transport dataset",
    "owner": "Publishing agency",
    "retrieved_on": "2026-11-02",
    "coverage": "Routes and service events for stated period",
    "licence": "Check source terms before reuse",
    "known_limitations": ["Possible missing events", "Definitions may change"]
}
print(source_record)
```

## 3. Professional application
Keep claims evidence-based. Document sources, assumptions, licences, decisions and limitations. A portfolio project should be understandable and reproducible without access to private data or undocumented local files.

## 4. Guided practice
Assess two potential sources for a project. Compare coverage, freshness, definitions, missingness, licence and collection bias. Choose one and document why it is fit for the question.

## 5. Independent practice
Create the corresponding artefact in your project repository. Ask another person to review it and record what was unclear or incomplete.

## 6. Knowledge check
1. What is the purpose of this professional practice?
2. What evidence should be preserved?
3. Which risks or constraints need to be disclosed?
4. How will another person verify the work?

## Lesson summary
Professional data science combines sound analysis with ethical judgement, reproducible practice and clear communication.