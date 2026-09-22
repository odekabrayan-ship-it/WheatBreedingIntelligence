# Scientific Specification

## Scientific Objective

Develop and validate a computational framework that integrates wheat genomic, phenotypic, environmental, and experimental information to support prediction and interpretation of performance under defined climate-stress conditions.

## Central Scientific Question

How can integrated genomic, phenotypic, and environmental information be used to generate reliable and interpretable predictions that support climate-resilient wheat breeding?

## Scientific Principle

The scientific target must be defined from the characteristics of the available wheat datasets.

The project will not assume that "climate resilience" is a single measurable trait.

A specific measurable target must be selected, such as an appropriate yield-related trait, stress response measure, stability measure, or another scientifically justified phenotype.

## Data Domains

The project may integrate:

- Genomic data
- Phenotypic data
- Environmental data
- Experimental design information
- Genotype information
- Location information
- Year information
- Management information
- Historical breeding information where available

## Genotype × Environment

Genotype × environment interaction is an important scientific component where sufficient data are available.

Validation should attempt to reflect realistic breeding scenarios.

Possible validation scenarios include:

- Unseen genotypes
- Unseen environments
- Unseen genotype-environment combinations

The exact validation design will depend on the available dataset structure.

## Modelling

The project should compare appropriate baseline statistical/genomic approaches with machine-learning approaches.

Potential methods may include:

- Linear or regularized statistical models
- Genomic prediction approaches
- Random Forest
- Gradient-boosting methods
- XGBoost where justified
- Other methods justified by the dataset

Deep learning should only be introduced if scientifically justified by the data and research question.

## Data Fusion

The project should investigate whether combining data domains provides useful predictive information.

Possible comparisons include:

A. Genomic information alone

B. Phenotypic/environmental information

C. Genomic + phenotypic information

D. Genomic + phenotypic + environmental information

The precise fusion architecture will be selected after examining the data.

## Explainable AI

Explainable AI methods will be used to investigate which input features contribute to model predictions.

Explanations must not automatically be interpreted as biological causality.

An important model feature is not necessarily a causal biological factor.

Where possible, important genomic signals should be examined against existing biological knowledge and relevant QTL, GWAS, or candidate-gene information.

## Validation

Model validation must minimize data leakage and overfitting.

Performance should be assessed using appropriate metrics for the selected target.

The validation strategy must reflect realistic use of the system by breeders.

## Scientific Integrity

The system must distinguish between:

- prediction
- association
- explanation
- biological interpretation
- causation

The project must not claim biological causation solely from machine-learning feature importance.

## Research Output

The MSc research should produce:

1. A scientifically validated analytical framework
2. A functional prototype
3. Reproducible computational workflows
4. Scientific results suitable for academic publication
5. A foundation for continued product development
