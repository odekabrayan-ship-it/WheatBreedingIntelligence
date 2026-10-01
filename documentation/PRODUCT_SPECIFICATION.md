# WheatBreeding Intelligence Platform

## Working Product Name

WheatBreeding Intelligence Platform (WheatBI)

## Product Purpose

WheatBI is intended to become a practical, scalable research and breeding decision-support platform for wheat breeding programmes.

The platform will integrate wheat genomic, phenotypic, environmental, and experimental data and transform them into scientifically interpretable information that can support breeding and research decisions.

The long-term product is not limited to an MSc thesis, a publication, or a single machine-learning model.

The MSc represents the first research and development phase of the product.

## Core Problem

Wheat breeders and researchers work with large and complex datasets originating from genomics, phenotyping, field experiments, environmental observations, historical breeding records, and other sources.

These data are often fragmented across files, analytical environments, databases, and research projects.

WheatBI aims to provide an integrated workflow for transforming these data into reproducible analyses, predictions, explanations, and breeding-support information.

## Initial Product Use Case

The first prototype will focus on climate-resilience-related wheat breeding intelligence.

The precise prediction target will be defined after examination of the real wheat datasets available to the research project.

The initial system should eventually support:

1. Data ingestion
2. Data validation
3. Data quality control
4. Genomic data processing
5. Phenotypic data processing
6. Environmental data processing
7. Data integration
8. Statistical modelling
9. Machine-learning modelling
10. Genotype × environment analysis
11. Prediction
12. Explainable AI
13. Uncertainty assessment
14. Candidate-line analysis
15. Reproducible reporting

## DatasetVersion and Provenance Architecture

DatasetVersion supports the platform’s long-term scientific requirements for reproducibility, traceability, provenance, and version history. In the intended architecture, a Dataset can contain multiple DatasetVersion entries, each representing a distinct, time-stamped state of the underlying scientific data. This creates a clear chain from a registered Dataset to the exact data state used for downstream analyses.

This is intended to support reliable linkage between analyses and the exact data state used, including downstream quality control, processed datasets, modelling, and breeding decision support. The model is therefore an architectural foundation for provenance and reproducibility, even though the operational capabilities are not yet implemented in the current product scope.

DatasetVersion is not currently a full operational system for upload processing, storage management, automated validation, or machine-learning workflows. Instead, it formalizes the data-model expectation that analyses can eventually be connected to a specific DatasetVersion, with an associated checksum for identity/integrity, and a clear record of what changed across versions.

The design must remain scientifically precise: version history and SHA-256 checks support data identity, provenance, and integrity, but they do not guarantee biological validity, data quality, or scientific interpretation. Those remain separate scientific assessments that must be performed by researchers and analysis workflows.

## Intended Users

Initial users:

- Wheat breeders
- Plant breeding researchers
- Wheat geneticists
- MSc researchers
- PhD researchers
- Research institutions

Future users may include:

- National breeding programmes
- Universities
- Agricultural research organizations
- Seed companies
- International research organizations
- Other crop breeding programmes

## Product Principle

WheatBI is a decision-support system.

It does not replace scientific judgement or breeders.

The platform should provide evidence, predictions, explanations, uncertainty, and analytical context so that qualified researchers can make informed decisions.

## Long-Term Vision

The long-term system should become a broader breeding intelligence platform capable of supporting multiple wheat breeding programmes and, eventually, potentially other crops.

The architecture must therefore be extensible and must not be hard-coded to one dataset or one machine-learning algorithm.

