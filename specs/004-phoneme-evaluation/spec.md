# Feature Specification: Phoneme Evaluation

**Feature Branch**: `004-phoneme-evaluation`  
**Created**: 2026-02-24  
**Status**: Completed  
**Input**: PC-GITA corpus, webMAUS CSV phoneme alignments, `PCGITAtoPD_mapping.csv` metadata (Sex, Age, H/Y).

## User Scenarios & Testing

### User Story 1 - Phoneme Duration Statistics (Priority: P1)
As a researcher, I want to calculate the mean and variance of phoneme durations to identify acoustic differences between PD and HC speakers.

**Acceptance Scenarios**:
1. **Given** phoneme alignment CSVs, **When** processed, **Then** the system MUST extract durations and apply **Z-score outlier filtering (Z=3)** to ignore non-standard alignments.
2. **Given** metadata, **When** calculating statistics, **Then** the system MUST group results by Status (PD/HC) and Sex (M/F) into a **Wide Statistics Table**.

---

### User Story 2 - Comparative Visualization (Priority: P2)
As a researcher, I want to visualize the distribution of phoneme durations using effect size metrics.

**Acceptance Scenarios**:
1. **Given** phoneme statistics, **When** visualizing, **Then** the system MUST rank phonemes by **Cohen's d** effect size.
2. **Given** the rankings, **When** generating boxplots, **Then** the system MUST include subplots for **Cohen's distance** and **Sample Counts**.
3. **Given** the need for detail, **Then** the system MUST provide stratified histograms for the top discriminative phonemes.

---

### User Story 3 - Parkinson's Disease Classification (Priority: P1)
As a researcher, I want to classify speakers as PD or HC using phoneme duration profiles and demographic info.

**Acceptance Scenarios**:
1. **Given** phoneme data, **When** building features, **Then** the system MUST construct **speaker-level** feature vectors (one vector per individual).
2. **Given** classification tasks, **When** training models (LR, MLP, HGBT), **Then** the system MUST evaluate performance both **with and without Sex** as an additional feature.
3. **Given** final results, **Then** the system MUST generate a **Per-Speaker Summary** table showing ground truth, predictions, and probabilities, sorted by Speaker ID.

## Requirements

### Functional Requirements
- **FR-001**: Load alignment data from 5 tasks: `ddk`, `monologue_split`, `readtext_split`, `sentences_cleaned`, and `words_merged`.
- **FR-002**: Implement Z-score outlier filtering and technical token filtering (`<usb>`, `<p:>`).
- **FR-003**: Calculate mean and variance of durations and Cohen's d effect sizes.
- **FR-004**: Generate long-form and wide-form summary CSV reports.
- **FR-005**: Produce enhanced stratified boxplots with a fixed Y-axis (0-0.25s) for consistency.
- **FR-006**: Implement a speaker-level classification pipeline using 10-fold StratifiedGroupKFold.
- **FR-007**: Provide an interactive visualization notebook with LaTeX-formatted equations.

## Success Criteria
- **SC-001**: Successful processing of all PC-GITA alignment data.
- **SC-002**: AUC and Accuracy reported for all task subsets and aggregated data.
- **SC-003**: Detailed per-speaker table with color-coded results.
