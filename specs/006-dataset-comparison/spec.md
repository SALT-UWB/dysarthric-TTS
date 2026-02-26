# Feature Specification: Dataset Comparison

**Feature Branch**: `dataset_comparison`  
**Created**: 2026-02-26  
**Status**: Completed  
**Input**: 
- Reference corpus (e.g., `datalocal/PC-GITA_v260210_24kHz`)
- Test corpus (e.g., `datalocal/genPC-GITA_ZipVoice-CML_ref-CML-wavLM`)
- Task directories: `ddk`, `monologue_split`, `readtext_split`, `sentences_cleaned`, `words_merged`
- File triplets per recording: WAV (audio), txt (transcription), csv (phoneme alignment)
- WavLM embeddings: Stored in `{corpus_root}/speaker_embeddings/wavLM`
- Metadata: PC-GITA speaker mapping (PD vs HC) including H/Y severity.

## User Scenarios & Testing

### User Story 1 - Dataset Integrity and Parallelism (Priority: P1)
As a researcher, I want to verify that my synthetic dataset is a true parallel version of the original corpus.

**Acceptance Scenarios**:
1. **Given** two dataset directories, **When** checked, **Then** the system MUST report any missing audio (.wav) and alignment (.csv) files.
2. **Given** parallel file pairs, **When** compared, **Then** the system MUST verify that transcriptions (.txt) are identical and log content mismatches.
3. **Given** audio files, **When** analyzed, **Then** the system MUST calculate duration and alert on differences > 50% relative to the reference.

---

### User Story 2 - Embedding Distance Analysis (Priority: P1)
As a researcher, I want to quantify how similar the synthetic audio is to the original in the WavLM embedding space.

**Acceptance Scenarios**:
1. **Given** WavLM embeddings for reference and test samples, **When** comparing, **Then** the system MUST calculate the distance between each parallel pair.
2. **Given** distances, **When** aggregating, **Then** the system MUST calculate mean distances and variances per speaker and per task group.
3. **Given** speaker metadata, **When** reporting, **Then** the system MUST distinguish between HC and PD groups.

---

### User Story 3 - Phoneme Duration and Alignment Fidelity (Priority: P1)
As a researcher, I want to evaluate the temporal fidelity of synthetic speech at the phoneme level.

**Acceptance Scenarios**:
1. **Given** phoneme alignment CSVs, **When** compared, **Then** the system MUST calculate the difference in duration for each parallel phoneme.
2. **Given** alignments, **When** analyzed, **Then** the system MUST identify missing phonemes in the synthetic dataset.
3. **Given** metrics, **When** aggregating, **Then** the system MUST report these differences per task group and speaker group (HC/PD).

---

### User Story 4 - Visual Comparative Reporting (Priority: P2)
As a researcher, I want to visualize the comparison results to quickly identify patterns and outliers.

**Acceptance Scenarios**:
1. **Given** comparison data, **When** generating a notebook, **Then** the system MUST provide tables for mean distances and variances.
2. **Given** speaker-level data, **When** plotting, **Then** the system MUST show differences across speakers for each task group.

## Requirements

### Functional Requirements
- **FR-001**: Implement a data integrity script to check file existence and transcription identity across reference and test directories.
- **FR-002**: Calculate audio duration for all files and identify significant length discrepancies.
- **FR-003**: Load WavLM embeddings from `{corpus_root}/speaker_embeddings/wavLM` for parallel comparison.
- **FR-004**: Calculate pairwise distances (e.g., Euclidean or Cosine) between parallel embeddings.
- **FR-005**: Analyze phoneme duration differences from CSV alignment files.
- **FR-006**: Identify missing phonemes in the test dataset relative to the reference.
- **FR-007**: Aggregate all metrics (duration, embedding distance, phoneme diffs) by Speaker, Task Group, and Health Status (PD/HC).
- **FR-008**: Provide a Jupyter notebook (`dataset_comparison_viz.ipynb`) for visualization of distances, variances, and speaker-level trends.

## Success Criteria
- **SC-001**: 100% coverage of file existence and transcription checks for the specified tasks.
- **SC-002**: Generation of a comprehensive distance report (embeddings and phonemes) for all speakers.
- **SC-003**: Interactive visualization notebook showing clear distinction between HC and PD distributions where applicable.
