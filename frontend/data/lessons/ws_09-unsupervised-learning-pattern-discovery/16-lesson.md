# Lesson 16: Unsupervised Learning Project

## Learning outcomes

By the end of this lesson, you should be able to Deliver a reproducible unsupervised project with data provenance, preprocessing, method comparison, stability checks, profiles or anomaly review, limitations and a justified recommendation.

![A complete unsupervised learning workflow](/course-assets/ws09/clustering-concepts.svg)

## 1. Core explanation
The final project applies an unsupervised method to a dataset with a defensible analytical purpose. Choose clustering, dimensionality reduction, anomaly detection or association analysis. Define the observation unit and feature meaning. Explain why an unsupervised method is appropriate and what decision or investigation it supports.

Prepare data carefully, justify scaling and encoding, compare parameters or methods and validate stability. Profile clusters in original units or investigate flagged anomalies. Include visuals that clarify structure without implying more certainty than the method supports.

Deliver a reproducible repository, data dictionary, analysis, evaluation, report and limitations. State whether the result is suitable for action, exploratory only or inconclusive. Do not label an anomaly as fraud or a cluster as a real customer type without independent evidence.

## 2. Worked Python example
Run in VS Code. Install packages with `python -m pip install numpy pandas matplotlib scipy scikit-learn`.

```python
# Project deliverables
# README with problem and purpose
# Data source, licence and data dictionary
# Reproducible preprocessing and analysis
# At least two methods or parameter settings
# Validation and stability analysis
# Cluster profiles or anomaly review
# Limitations and recommended next step
```

## 3. Interpretation
Describe the feature representation, model settings and meaning of the output. Validate patterns in original units. Cluster IDs are arbitrary and anomaly flags are not proof of wrongdoing.

## 4. Guided practice
Submit the project with a five-minute presentation. Rubric: problem framing 15%, data preparation 20%, method selection 15%, validation and stability 20%, interpretation 15%, reproducibility and limitations 15%.

## 5. Independent practice
Apply the method to a dataset. Compare at least two parameter settings or methods, profile results and document stability, limitations and possible actions.

## 6. Knowledge check
1. What structure is the method attempting to discover?
2. Which assumptions are introduced by the representation or distance?
3. How will you assess stability and usefulness?
4. What should not be inferred from the output?

## Lesson summary
Unsupervised algorithms find patterns according to mathematical definitions. Stability, interpretation and practical validation determine whether those patterns deserve to be used.

## Final project specification and marking guide

Choose a dataset with a clear source, licence and data dictionary. Suitable topics include retail, public services, education, sensors or other non-sensitive data. Prefer public or synthetic data for a learning project. Define the observation unit and explain why an unsupervised method suits the question.

The report must include: problem framing and intended use; data source, licence, row meaning and feature definitions; missingness, duplicates and data-quality findings; preprocessing decisions and justification; comparison of at least two methods or materially different settings; validation and stability checks; original-unit profiles or careful anomaly review; visuals with clear captions; and limitations, risks and next steps.

Assessment rubric: problem framing and provenance 15%; preparation and feature reasoning 20%; method selection and implementation 15%; validation and stability 20%; interpretation and communication 15%; reproducibility, ethics and limitations 15%.

Submit a README with setup instructions, a reproducible notebook or script, a data dictionary, preprocessing record, method comparisons, validation results and a report that separates observation from interpretation. State clearly what the model cannot prove.

**Reflection:** If the result is unstable or not useful, what would you recommend instead? Strong analysts are willing to reject a model when the evidence does not justify its use.

### Project extension: make the result reproducible

Organise the project so another learner can reproduce it. Separate raw data, processed data, notebooks or scripts, figures and the written report. Do not overwrite the raw source. Include setup commands and package versions, and explain how to obtain the dataset legally. If the data cannot be redistributed, document the source and provide a small synthetic example.

The final presentation should show the question, observation unit, feature decisions, method comparison, validation, profile and limitations. A chart needs labelled axes, a legend where relevant and a caption that explains the finding and caveat. A screenshot without interpretation is not an analytical result.

Finish with a recommendation that matches the evidence: proceed to a controlled test, collect better features, monitor a pattern, use a simpler method or conclude that no reliable structure was found.
