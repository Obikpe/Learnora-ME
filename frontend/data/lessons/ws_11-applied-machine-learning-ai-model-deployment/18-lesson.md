# Lesson 18: Generative AI and Foundation Models

## Learning outcomes

By the end of this lesson, you should be able to Explain foundation models and generative AI at a conceptual level; identify suitable and unsuitable tasks; recognise hallucination, privacy and cost risks; and review prompts and outputs before use.

## 1. Core explanation
A foundation model is trained on broad data and can be adapted to many tasks. Large language models (LLMs) predict text tokens based on context; other foundation models work with images, audio or multimodal inputs. Generative AI creates new content, but fluent output is not the same as factual correctness.

Important concepts include tokens, context window, pretraining, instruction tuning, inference and temperature. A prompt provides task instructions and context. Retrieval-augmented generation (RAG) supplies relevant external documents to a model at response time. Fine-tuning changes model parameters using additional examples; it is different from simply providing examples in a prompt.

Use generative systems with verification, privacy controls and human oversight. They can hallucinate, reproduce bias, expose sensitive content or be manipulated by untrusted input. Do not send confidential data to a service without checking its terms and organisational policy.

## 2. Worked example
Run the Python example in VS Code. Install relevant packages with `python -m pip install numpy pandas scipy scikit-learn`. Cloud services and hosted models are not required for the local examples.

```python
prompt = """You are a careful assistant.
Summarise the following policy excerpt in three bullet points.
If the excerpt does not contain an answer, say so.
Excerpt: "Learners may submit assignments until 5 pm on Friday."
Question: What is the submission deadline?"""
print(prompt)  # Send to an approved model client only after reviewing data policy.
```

## 3. Operational interpretation
State what the example demonstrates and what it does not demonstrate. Distinguish a local prototype from a production deployment. Document dependencies, input/output contracts, data handling, failure modes and model version.

## 4. Guided practice
List three appropriate and three inappropriate uses of a generative model in a data-science workflow. For each, identify how output will be verified and what information must not be shared.

## 5. Independent practice
Add the lesson's control or component to your own small ML application. Write a short runbook explaining how to test it, monitor it and respond when it fails.

## 6. Knowledge check
1. What can fail outside the model itself?
2. What should be logged and what should remain private?
3. How would you detect a change in behaviour?
4. What is the rollback or fallback plan?

## Lesson summary
Production ML is an engineered service with explicit contracts, versioning, monitoring, security and human accountability. A model score alone is not evidence of production readiness.