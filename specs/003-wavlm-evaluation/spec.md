# Feature Specification: wavLM-evaluation

**Feature Branch**: `wavLM_evaluation`  
**Created**: 2026-02-23  
**Status**: Completed  
**Input**: PC-GITA corpus, WavLM embeddings (microsoft/wavlm-base-plus-sv), `PCGITAtoPD_mapping.csv` metadata (Sex, Age, H/Y).

## User Scenarios & Testing

### User Story 1 - Multi-Level Embedding Analysis (Priority: P1)
Analyze WavLM embeddings across tasks (DDK, monologue, readtext, sentences, words) for PD and HC speakers.

**Acceptance Scenarios**:
1. **Given** embeddings, **When** processed, **Then** the system MUST correctly identify Speaker ID, Status, and Group from filenames (including 4-word patterns for 'words' group).
2. **Given** speaker data, **When** analyzed, **Then** the system MUST calculate centroids per group and global speaker centroids (excluding DDK for HC consistency).

---

### User Story 2 - Centroid-Based Speaker Assignment (Priority: P1)
Evaluate speaker identity preservation by assigning samples to the nearest pre-calculated group centroid.

**Acceptance Scenarios**:
1. **Given** classification logic, **When** executed, **Then** the system MUST report accuracy and TOP 5 intruders (speaker+group) with percentages in `centroid_speaker_assignment.ipynb`.

---

### User Story 3 - Machine Learning Trait Prediction (Priority: P1)
Predict Sex, Age, and Health Status using advanced ML models in `ml_classification_analysis.ipynb`.

**Acceptance Scenarios**:
1. **Given** embeddings and metadata, **When** training LR, Ridge, MLP, and HGBT models, **Then** the system MUST use StratifiedGroupKFold (n=10) to prevent speaker leakage and ensure balanced groups.
2. **Given** age prediction, **Then** the system MUST visualize age distribution and absolute error distribution via histograms (HGBT model).
3. **Given** PD/HC detection, **Then** the system MUST exclude DDK samples, evaluate multiple models (LR, MLP, HGBT), and provide styled per-speaker summaries.

## Requirements

### Functional Requirements
- [x] FR-001: Load `.pt` files and integrate mapping metadata (Sex, Age, H/Y).
- [x] FR-002: Identify task groups including the 4+ word pattern for spontaneous word sequences.
- [x] FR-003: Calculate hierarchical centroids (Global mean excludes DDK).
- [x] FR-004: Implement Centroid-Based Speaker Assignment with Top 5 intruder detection.
- [x] FR-005: Implement ML experiments for Sex (LR, MLP, HGBT), Age (Ridge, HGBT), and Status (LR, MLP, HGBT).
- [x] FR-006: Use StratifiedGroupKFold (n=10) for robust cross-validation.
- [x] FR-007: Implement aggregated speaker-level classification using Majority Vote and Average Probability methods.
- [x] FR-008: Visualize results with hierarchical spider plots, histograms, and styled pandas tables.

## Success Criteria
- **SC-001**: 100% metadata integration for all processed speakers.
- **SC-002**: Successful execution of all ML pipelines with progress tracking (tqdm).
- **SC-003**: Fully English interactive notebooks for all analysis phases.
