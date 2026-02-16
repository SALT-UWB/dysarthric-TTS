# Feature Specification: segment-pcgita-sentences

**Feature Branch**: `001-segment-pcgita-sentences`  
**Created**: 2026-02-12  
**Status**: Draft  
**Input**: User description: "Specify Phase-1 sentence/segment splitting for a preprocessed PC-GITA subset..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deterministic Sentence Splitting (Priority: P1)

As a researcher, I want to split long audio recordings into individual sentences based on phoneme alignment metadata, so that I can prepare a clean dataset for TTS training.

**Why this priority**: Core deliverable. Without splitting, downstream Phase-2 training cannot begin.

**Independent Test**: Can be fully tested by running `split_sentences.py` on a dummy recording with a known alignment CSV and verifying that output files match the expected midpoint-pause cuts.

**Acceptance Scenarios**:

1. **Given** a WAV file and a corresponding alignment CSV, **When** the script detects a pause token followed by a capitalized word, **Then** it MUST cut the audio and metadata at the midpoint of that pause.
2. **Given** a segment starting at sample X, **When** the segmented CSV is written, **Then** all BEGIN sample values MUST be shifted by -X so the segment starts at 0.

---

### User Story 2 - Automated Dataset Statistics (Priority: P2)

As a data scientist, I want to generate a report of the segmented dataset, including word counts, audio duration, and silence distributions (leading/trailing), so that I can validate the balance and quality of my training data.

**Why this priority**: Essential for quality assurance and scientific reporting.

**Independent Test**: Can be tested by running the `split_sentences_stats.ipynb` notebook on an output directory and verifying that HC/PD counts and silence distributions are generated.

**Acceptance Scenarios**:

1. **Given** a directory of segmented files, **When** I run the validation notebook, **Then** it MUST flag any incomplete triples (missing wav, txt, or csv).
2. **Given** segmented files with names like "001PD_..." and "041YHC_...", **When** stats are computed, **Then** they MUST be correctly categorized into Patient (PD) and Healthy Control (HC) groups.
3. **Given** segmented CSVs, **When** the stats notebook is run, **Then** it MUST calculate and visualize the distribution (min, max, mean) of leading and trailing silence.

---

### User Story 3 - Monologue Transcription Generation (Priority: P2)

As a researcher, I want to automatically generate transcripts for the monologue recordings by mapping them to the provided master metadata, so that I have a complete dataset for the monologue subset.

**Acceptance Scenarios**:

1. **Given** a directory of monologue WAV files, **When** I run the mapping script, **Then** it MUST generate a corresponding TXT file for each WAV.
2. **Given** raw transcript text, **When** processed, **Then** it MUST be lowercase, have sentence-level capitalization, and no spaces before punctuation.

---

### User Story 4 - Reproducible Environment Setup (Priority: P3)

As a developer, I want clear instructions and a standardized `.venv` setup, so that I can run the preprocessing pipeline consistently across different machines.

**Why this priority**: Ensures long-term maintainability and reduces "it works on my machine" errors.

**Independent Test**: Can be tested by following the README instructions to create and activate `.venv` and then successfully importing `data_prepare` logic.

**Acceptance Scenarios**:

1. **Given** a fresh clone of the repo, **When** I run the setup commands, **Then** a `.venv` directory MUST be created and all dependencies (ruff, mypy, pytest, librosa, pandas) installed.

---

### Edge Cases

- **Missing Alignment**: How does the system handle a WAV file without a corresponding CSV? (Result: FAIL LOUDLY with log entry).
- **Sampling Rate Mismatch**: If a WAV is not 24000 Hz and no override is provided? (Result: FAIL LOUDLY).
- **Overlapping Segments**: If timing in CSV exceeds audio length? (Result: FAIL LOUDLY).
- **Long Mid-sentence Pause**: If a pause is 1.5s but no capitalized word follows? (Result: Split anyway based on the 1.0s threshold rule).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST read sampling rate directly from WAV headers using a library like `soundfile` or `librosa`.
- **FR-002**: System MUST use the WAV sampling rate to convert alignment sample indices to seconds.
- **FR-003**: The split logic MUST trigger a cut at the midpoint of `<p:>` tokens when followed by an uppercase ORT value.
- **FR-004**: System MUST trigger a cut on any pause duration > 1.0 second (configurable).
- **FR-005**: Segmented CSVs MUST preserve all columns from the original header but shift BEGIN values.
- **FR-006**: The notebook MUST save statistics to a machine-readable JSON/CSV in a `reports/` directory.
- [x] FR-007: Scripts MUST handle Windows backslashes and POSIX paths transparently.
- [x] FR-008: System MUST calculate and visualize leading and trailing silence distributions for all segments.
- [x] FR-009: System MUST map monologue audio IDs to transcripts using the `PCGITAtoPD_mapping.csv` master file.
- [x] FR-010: Transcript cleaning MUST enforce lowercase, sentence-start capitalization, and removal of spaces before punctuation.

### Key Entities *(include if feature involves data)*

- **Base Recording**: The source triple (WAV, TXT, CSV) from the raw subset.
- **Segment**: The output triple (WAV, TXT, CSV) representing a single sentence or long-pause-delimited unit.
- **Phoneme Alignment**: Metadata rows including BEGIN, DURATION, TOKEN, and ORT.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of segmented WAV files MUST be playable and contain the audio corresponding to the TXT/CSV text.
- **SC-002**: The sum of segment durations (plus mid-segment pauses) MUST equal the source WAV duration within a 1-sample tolerance.
- **SC-003**: Processing a 100-file subset MUST complete in under 5 minutes on standard hardware.

## Ethics & Licensing *(mandatory)*

- **EL-001**: Feature MUST NOT use real PC-GITA data for automated tests.
- **EL-002**: Data handling MUST prevent re-identification of participants.
- **EL-003**: Outputs MUST NOT reproduce individual speaker identities (no cloning).
- **EL-004**: Preprocessing code MUST assume raw data resides in `datalocal/` which is ignored by git.
