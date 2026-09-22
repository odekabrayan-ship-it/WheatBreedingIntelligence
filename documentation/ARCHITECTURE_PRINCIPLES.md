# Architecture Principles

## 1. Product Before Model

The platform is a breeding and research intelligence system.

Machine learning is one component of the system, not the entire product.

## 2. Scientific Correctness Before Complexity

The simplest scientifically defensible method should be preferred over unnecessary technical complexity.

## 3. Data-Driven Target Definition

The prediction target must be selected after understanding the available real-world wheat data.

## 4. Replaceable Analytical Engines

The platform must allow different statistical and machine-learning models to be added, compared, replaced, or removed without rebuilding the entire application.

## 5. Reproducibility

Every major analysis should record relevant:

- Dataset version
- Parameters
- Model
- Validation strategy
- Software version
- Results

## 6. Explainability

Where AI models are used, the platform should provide interpretable information about model behaviour.

## 7. Uncertainty

Predictions should be accompanied by appropriate uncertainty or confidence information where scientifically possible.

## 8. Breeder-Centered Design

The user interface should focus on scientific and breeding questions rather than exposing unnecessary software complexity.

## 9. Scalable Architecture

The prototype should be capable of evolving from a single research project into a multi-project and multi-institution platform.

## 10. Data Separation

Raw data should be preserved.

Processed data should be separated from raw data.

Derived analytical results should be traceable to their source datasets.

## 11. Security and Privacy

Sensitive research data and institutional information must be protected.

Authentication, authorization, access control, and secure deployment will be introduced as the product matures.

## 12. Human Decision Support

The platform should support researchers and breeders rather than automatically making irreversible scientific or breeding decisions.
