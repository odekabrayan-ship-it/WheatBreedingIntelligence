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

## Dataset Domain

A Dataset is a registered scientific data asset that belongs to a WheatBI project. It represents a known data source or study resource in the platform but is intentionally not the same as a physical uploaded file or a versioned dataset artifact.

A Dataset may have many DatasetVersion records over time. Each DatasetVersion represents an immutable, reproducible state of a Dataset at a particular point in time. The relationship is one-to-many from Dataset to DatasetVersion, with each DatasetVersion belonging to exactly one Dataset.

DatasetVersion exists to establish scientific provenance and reproducibility. For example, a genotype dataset may begin as an original release and later be replaced by a materially corrected release with changes to sample identifiers. Each materially distinct underlying data state should be represented as a distinct DatasetVersion so that analyses can be linked to the exact data state used.

Version numbering is unique within a Dataset, not globally. The database rule will eventually enforce UNIQUE(dataset_id, version_number), so the following patterns are valid: Dataset A version 1 and version 2; Dataset B version 1 and version 2. The pattern Dataset A version 2 and Dataset A version 2 is invalid.

The initial DatasetVersion data model is defined by the following fields:

- id: UUID unique identifier
- dataset_id: foreign key identifying the parent Dataset
- version_number: integer identifying the version within its Dataset
- description: description of what the version represents or what changed
- file_name: name of the associated data file
- file_format: file format such as CSV, TSV, VCF, XLSX, etc.
- file_size_bytes: size of the associated physical file in bytes
- checksum_sha256: SHA-256 checksum identifying the exact file contents
- row_count: number of records/rows where applicable
- column_count: number of columns where applicable
- status: initial lifecycle status
- created_at: creation timestamp
- updated_at: last metadata update timestamp

The initial DatasetVersion status values are:

- REGISTERED
- PROCESSING
- READY
- FAILED
- ARCHIVED

These are aligned with the initial Dataset lifecycle and are not intended to represent broader workflow semantics beyond the foundational metadata model.

Scientific integrity requires that a DatasetVersion represent a reproducible state. Once a version is established as an operational or ready scientific artifact, its core identity must not be silently replaced by different underlying data. If the data change materially, a new DatasetVersion must be created instead of overwriting the prior version. A version that previously had checksum ABC... must not silently become checksum XYZ... without the creation of a new version entry.

SHA-256 is included so WheatBI can later establish the exact physical artifact associated with a DatasetVersion. This supports provenance and file identity/integrity checks. It does not prove scientific correctness, biological validity, or overall data quality. Those remain separate scientific assessments.

The initial DatasetVersion architecture intentionally excludes file_path or provider-specific storage fields. A local filesystem path, S3 bucket field, Azure Blob field, or any other cloud-provider-specific storage abstraction is intentionally not included at this stage. Storage abstraction will be designed separately in a later phase.

DatasetVersion is not yet a system for upload UI, data ingest processing, cloud storage, genomic parsing, phenotypic parsing, environmental parsing, automated quality control, machine learning, authentication, authorization, permissions, collaboration, or advanced validation. At this stage, it is a provenance and data-model foundation for tracking exact data states over time.

The intended future scientific provenance chain is:

Project
↓
Dataset
↓
DatasetVersion
↓
Quality Control
↓
Processed Dataset
↓
Analysis
↓
Model
↓
Prediction
↓
Breeding Decision Support

This chain represents intended future architecture, not currently implemented functionality.

Initial dataset types are:

- GENOMIC
- PHENOTYPIC
- ENVIRONMENTAL
- EXPERIMENTAL
- DERIVED

Initial dataset statuses are:

- REGISTERED
- PROCESSING
- READY
- FAILED
- ARCHIVED

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
