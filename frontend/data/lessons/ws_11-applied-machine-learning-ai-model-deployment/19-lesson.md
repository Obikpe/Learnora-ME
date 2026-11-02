# Lesson 19: Prompting, Embeddings and Retrieval Concepts

## Learning outcomes
Explain the production concept, implement the worked example where applicable, and identify reliability, security and governance requirements.

## 1. Core explanation
Prompting gives a model instructions, context and an output format. Good prompts define the task, audience, constraints and evidence boundaries. Few-shot prompting includes examples. Structured-output prompting requests a schema, but the output must still be validated.

Embeddings represent text or other content as numeric vectors. Similarity search retrieves items whose vectors are close under a chosen metric. Retrieval-augmented generation uses a search step to provide relevant source passages to a generative model. Retrieval can improve grounding but cannot guarantee that the model uses sources correctly.

A RAG system requires document ingestion, chunking, embedding, indexing, retrieval, context construction and answer generation. Evaluate retrieval separately from generation. Cite sources, handle missing evidence and protect private documents. Prompt injection can appear inside retrieved content; treat retrieved text as data, not trusted instructions.

## 2. Worked example
Run the Python example in VS Code. Install relevant packages with `python -m pip install numpy pandas scipy scikit-learn`. Cloud services and hosted models are not required for the local examples.

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

documents = [
    "Model monitoring tracks prediction quality and service health.",
    "Feature engineering creates useful variables from raw data.",
    "Data drift occurs when input distributions change."
]
query = ["How can we detect changes in incoming model data?"]
vectorizer = TfidfVectorizer()
matrix = vectorizer.fit_transform(documents + query)
scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
print(sorted(zip(scores, documents), reverse=True))
```

## 3. Operational interpretation
State what the example demonstrates and what it does not demonstrate. Distinguish a local prototype from a production deployment. Document dependencies, input/output contracts, data handling, failure modes and model version.

## 4. Guided practice
Explain the stages of a RAG workflow. Identify two ways retrieval can fail and two ways generated answers can still be wrong even when relevant documents are retrieved.

## 5. Independent practice
Add the lesson's control or component to your own small ML application. Write a short runbook explaining how to test it, monitor it and respond when it fails.

## 6. Knowledge check
1. What can fail outside the model itself?
2. What should be logged and what should remain private?
3. How would you detect a change in behaviour?
4. What is the rollback or fallback plan?

## Lesson summary
Production ML is an engineered service with explicit contracts, versioning, monitoring, security and human accountability. A model score alone is not evidence of production readiness.