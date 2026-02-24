# Research: Phoneme Evaluation

This document outlines the research and technical decisions for the phoneme evaluation subproject, focusing on acoustic differences between PD and HC speakers in the PC-GITA corpus.

## Decision: Phoneme Alignment Parsing
**Rationale**: webMAUS provides alignments in CSV format (standard for this project's pipeline). We need to reliably extract `phoneme`, `start`, and `end` times.
- **Implementation**: Use `pandas` for efficient CSV loading.
- **Handling**: Ensure consistency in phoneme labeling across different recording tasks.

## Decision: Outlier Detection (Alignment Error Filtering)
**Rationale**: Automatic alignment tools like webMAUS can produce errors, especially with dysarthric speech (e.g., misaligned segments, extremely long silences).
- **Implementation**:
  - Filter phonemes based on duration percentiles (e.g., ignore anything above 99th or below 1st percentile for a given phoneme type).
  - Use Z-score or IQR-based filtering per phoneme category.
- **Alternatives**: Manually verifying thousands of files is infeasible; statistical filtering is the standard approach.

## Decision: Feature Vector Design for Classification
**Rationale**: We need to represent a speaker's acoustic profile based on phoneme statistics.
- **Implementation**:
  - Calculate `mean` and `variance` for each phoneme observed for a speaker.
  - Since not all speakers produce all phonemes in all tasks, we will use a global phoneme list and fill missing values (e.g., with 0 or corpus mean).
  - Normalize features (StandardScaler) before classification.

## Decision: Classification Strategy
**Rationale**: Consistency with `embeddings_eval` is required.
- **Models**: Logistic Regression (LR), Multi-Layer Perceptron (MLP), and HistGradientBoosting (HGBT).
- **Validation**: `StratifiedGroupKFold` (n=10) to ensure speaker independence between folds.
- **Evaluation**: Per-sample accuracy and aggregated speaker-level metrics (Majority Vote, Average Probability).

## Decision: Visualization
**Rationale**: Histograms are requested for the top 10 discriminative phonemes.
- **Implementation**: Use `matplotlib` and `seaborn`.
- **Selection**: Use Cohen's d or similar effect size metric to identify the "most different" phonemes between PD and HC groups.
