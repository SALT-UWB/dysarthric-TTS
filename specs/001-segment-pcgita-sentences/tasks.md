---
description: "Task list for Phase-1 sentence splitting implementation"
---

# Tasks: segment-pcgita-sentences

**Input**: Design documents from `/specs/001-segment-pcgita-sentences/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Tests are requested in the specification (minimal dummy dataset + pytest).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel
- **[Story]**: US1 (Splitting), US2 (Notebook), US3 (Environment)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and virtual environment setup

- [x] T001 Create project structure per implementation plan (data_prepare/, tests/)
- [x] T002 [US3] Initialize Python .venv and install dependencies (librosa, pandas, soundfile, ruff, mypy, pytest, jupyter)
- [x] T003 [P] Configure linting and formatting (ruff.toml, pyproject.toml)
- [x] T004 [US3] Create setup instructions in README.md for .venv management

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core logic and test data available before splitting logic

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 [P] Create minimal synthetic dummy dataset in tests/data_prepare/dummy_data/ (WAV + TXT + CSV)
- [x] T006 Implement shared logging and configuration utilities in data_prepare/utils.py
- [x] T007 Implement audio metadata utility to extract sampling rate in data_prepare/audio_utils.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Deterministic Sentence Splitting (Priority: P1) 🎯 MVP

**Goal**: Batch process PC-GITA recordings into sentence segments based on alignments.

**Independent Test**: Run `split_sentences.py` on dummy data and verify output stems (_001, _002...) and midpoint cuts.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T008 [P] [US1] Create unit tests for midpoint calculation and sample-to-second conversion in tests/data_prepare/test_splitting.py
- [x] T009 [P] [US1] Create integration test for full splitting CLI in tests/data_prepare/test_splitting.py

### Implementation for User Story 1

- [x] T010 [US1] Implement CSV alignment parser with sample-to-second conversion in data_prepare/split_sentences.py
- [x] T011 [US1] Implement sentence boundary detection logic (uppercase ORT + pause midpoint) in data_prepare/split_sentences.py
- [x] T012 [US1] Implement audio slicing and file writing (WAV/TXT/CSV) with timing shifting in data_prepare/split_sentences.py
- [x] T013 [US1] Add "fail-loud" validation for sampling rate and audio duration consistency
- [x] T014 [US1] Add summary reporting (processed counts, word counts, skipped files) to CLI output

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Automated Dataset Statistics (Priority: P2)

**Goal**: Validate segmented dataset triples and generate group breakdowns (HC vs PD).

**Independent Test**: Run the notebook on segmented dummy data and verify the saved JSON report matches expectations.

### Implementation for User Story 2

- [x] T015 [US2] Implement triple validation logic (wav/txt/csv matching) in data_prepare/split_sentences_stats.ipynb
- [x] T016 [US2] Implement HC/PD categorization and statistical aggregation (word/sentence counts, audio duration) in data_prepare/split_sentences_stats.ipynb
- [x] T017 [US2] Implement machine-readable report export (JSON/CSV) to reports/ directory in data_prepare/split_sentences_stats.ipynb
- [x] T018 [US2] Implement leading/trailing silence distribution analysis and visualization in data_prepare/split_sentences_stats.ipynb
- [x] T019 [US3] Implement monologue-to-PD mapping logic in `get_monologue_transcription.py`
- [x] T020 [US3] Implement sentence-level capitalization and text normalization for monologue transcripts

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final quality checks and documentation

- [x] T018 [P] Run ruff/mypy validation on all data_prepare/ scripts
- [x] T019 Update quickstart.md with actual CLI usage examples and expected output logs

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on T001, T002.
- **Phase 3 (US1)**: Depends on T005, T006, T007.
- **Phase 4 (US2)**: Depends on Phase 3 (needs segmented output to validate).
- **Phase 5 (Polish)**: Depends on all stories.

### Implementation Strategy

1. **MVP First**: Complete Phase 1, 2, and 3 to have a working splitting CLI.
2. **Incremental**: Add User Story 2 (Notebook) once the CLI is producing stable outputs.
3. **Validation**: Use US2 notebook to validate US1 outputs.

---

## Parallel Opportunities

- T003 (Linting) and T004 (README) can run in parallel with T002.
- T005 (Dummy data) and T007 (Audio utils) can run in parallel.
- T008 and T009 (Tests) can be written simultaneously.
