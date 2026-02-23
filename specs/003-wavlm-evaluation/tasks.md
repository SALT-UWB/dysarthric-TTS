---
description: "Actionable tasks for hierarchical WavLM embedding evaluation"
---

# Tasks: wavLM-evaluation

**Input**: Design documents from `/specs/003-wavlm-evaluation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Status**: Completed (2026-02-23)

---

## Phase 1: Setup (Completed)
- [x] T001 Create project structure (embeddings_eval/)
- [x] T002 Initialize `embeddings_eval/__init__.py`
- [x] T003 Create `embeddings_eval/constants.py`

---

## Phase 2: Foundational (Completed)
- [x] T004 Implement filename parsing logic
- [x] T005 Implement `EmbeddingFile` and `Centroid` data classes
- [x] T006 Implement batch loading from `datalocal/`
- [x] T007 Implement cosine distance utility

---

## Phase 3: Analysis & Logic (Completed)
- [x] T008 [US1] Create unit tests in `tests/data_prepare/test_wavlm_logic.py`
- [x] T009 [US1] Implement hierarchical centroid calculation
- [x] T010 [US1] Implement distance logic (Sample vs Centroids)
- [x] T011 [US1] Implement neighbor search

---

## Phase 4: Reporting (Completed)
- [x] T012 [US2] Implement summary table generation
- [x] T013 [US2] Implement detailed report generation
- [x] T014 [US2] Create execution script `run_eval.py`
- [x] T024 [NEW] Create `report_tables.ipynb` for interactive browsing

---

## Phase 5: Visualization (Completed)
- [x] T015 [US3] Implement PCA and t-SNE projection
- [x] T016 [US3] Implement hierarchical spider-plot visualization
- [x] T017 [US3] Create `interactive_eval.ipynb`

---

## Phase 6: Machine Learning (Completed)
- [x] T025 [NEW] Implement Sex Classification experiments
- [x] T026 [NEW] Implement Age Prediction experiments
- [x] T027 [NEW] Implement PD/HC Detection experiments
- [x] T028 [NEW] Create `classification_analysis.ipynb`

---

## Phase 7: Polish & Documentation (Completed)
- [x] T021 Run `ruff check` validation
- [x] T022 Update documentation in `research.md`
- [x] T023 Update `quickstart.md` with notebook descriptions
