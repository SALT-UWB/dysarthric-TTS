# Development Plan - Phoneme Evaluation

Implementation of phoneme-based acoustic analysis and classification for PD detection.

## Phase 0: Research & Setup (Completed)
- [x] Research alignment parsing and outlier detection.
- [x] Define data model and entities.

## Phase 1: Data Ingestion & Preprocessing (Completed)
- [x] Implement `data_loader.py` with Z-score filtering and technical token removal.
- [x] Refine task directory scanning (root + `ali_phoneme`).

## Phase 2: Statistical Analysis & Reporting (Completed)
- [x] Implement `analyzer.py` with Cohen's d calculation.
- [x] Implement `reporter.py` with Long and Wide format support.
- [x] Implement `visualizer.py` with enhanced 3-subplot boxplots (Duration, Cohen's d, Count).

## Phase 3: Machine Learning Classification (Completed)
- [x] Implement `ml_classification.ipynb` with speaker-level aggregation.
- [x] Add classification experiment including **Sex** as a feature.
- [x] Implement **Per-Speaker Summary** with styled tables and probabilities.

## Phase 4: Validation & Visualization (Completed)
- [x] Create `statistics_visualization.ipynb` for interactive exploration.
- [x] Standardize Y-axis (0-0.25s) across all duration plots.
- [x] Document Z-score and Cohen's d methodology in notebooks.
