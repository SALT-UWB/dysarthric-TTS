# Data Model: Phoneme Evaluation

This document defines the key entities and data structures used in the phoneme evaluation subproject.

## Entities

### 1. Phoneme Sample
Individual phoneme occurrence extracted from a webMAUS alignment file.
- `speaker_id`: Unique identifier for the speaker.
- `task`: Task group (e.g., `ddk`, `monologue_split`).
- `phoneme`: Phoneme label (SAMPA or IPA).
- `start_time`: Offset in seconds.
- `end_time`: Offset in seconds.
- `duration`: Calculated as `end_time - start_time`.

### 2. Speaker Metadata
Loaded from `PCGITAtoPD_mapping.csv`.
- `speaker_id`: Matching `Code BD-Parkinson`.
- `sex`: `M` or `F`.
- `age`: Numeric value.
- `status`: `PD` (H/Y > 0) or `HC` (H/Y = 0).
- `hy_score`: Hoehn & Yahr score.

### 3. Phoneme Statistics (Aggregate)
Aggregated data used for reporting and visualization.
- `group`: (Total, HC, PD, Male, Female, Task-specific).
- `phoneme`: Label.
- `mean_duration`: Average duration for this group.
- `var_duration`: Variance of duration for this group.
- `count`: Number of samples.

### 4. Classification Feature Vector
Input for ML models.
- `speaker_id`: Identifier.
- `features`: Array of (mean, variance) pairs for each phoneme in the global set.
- `label`: `1` for PD, `0` for HC.

## Relationships
- **Speaker** produces many **Phoneme Samples** across different **Tasks**.
- **Metadata** is linked to **Speaker** via `speaker_id`.
- **Phoneme Samples** are aggregated into **Phoneme Statistics** and **Feature Vectors**.
