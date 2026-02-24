# Tasks: Phoneme Evaluation

Implementation tasks for phoneme-based acoustic analysis and classification of Parkinson's Disease.

## Phase 1: Setup
Goal: Initialize the project structure and common utilities.

- [x] T001 Create directory structure for `phoneme_evaluation/`
- [x] T002 Create `phoneme_evaluation/__init__.py`
- [x] T003 [P] Define shared constants (task names, paths) in `phoneme_evaluation/constants.py`
- [x] T004 [P] Implement common path utilities in `phoneme_evaluation/utils.py`

## Phase 2: Foundational
Goal: Implement data loading and preprocessing logic used by all user stories.

- [x] T005 Implement metadata mapping loader in `phoneme_evaluation/data_loader.py`
- [x] T006 Implement alignment CSV parser in `phoneme_evaluation/data_loader.py`
- [x] T007 [P] Implement outlier detection logic (Z-score/percentile filtering) in `phoneme_evaluation/data_loader.py`
- [x] T008 Integrate metadata and alignment loading into a unified `load_all_data` function in `phoneme_evaluation/data_loader.py`

## Phase 3: User Story 1 - Phoneme Duration Statistics (P1)
Goal: Calculate mean and variance of phoneme durations across groups.
Independent Test: Run a script that prints the summary table and verifies counts match the corpus.

- [x] T009 [US1] Implement statistical aggregator in `phoneme_evaluation/analyzer.py`
- [x] T010 [US1] Implement group-wise split logic (HC/PD, M/F, Task) in `phoneme_evaluation/analyzer.py`
- [x] T011 [US1] Implement summary table exporter in `phoneme_evaluation/reporter.py`
- [x] T012 [US1] Create execution script `phoneme_evaluation/run_stats.py` to generate `reports/phoneme_stats_summary.csv`

## Phase 4: User Story 3 - Parkinson's Disease Classification (P1)
Goal: Classify speakers as PD or HC using phoneme statistics.
Independent Test: Run the notebook and verify that Cross-Validation results are reported for all task subsets.

- [x] T013 [US3] Implement feature vector construction (mean/variance per phoneme) in `phoneme_evaluation/data_loader.py`
- [x] T014 [US3] Setup `phoneme_evaluation/ml_classification.ipynb` with standard imports and data loading
- [x] T015 [P] [US3] Implement StratifiedGroupKFold validation loop in `phoneme_evaluation/ml_classification.ipynb`
- [x] T016 [US3] Implement LR, MLP, and HGBT model pipelines in `phoneme_evaluation/ml_classification.ipynb`
- [x] T017 [US3] Implement speaker-level aggregation (Majority Vote, Avg Prob) in `phoneme_evaluation/ml_classification.ipynb`
- [x] T018 [US3] Generate comprehensive result summary table in `phoneme_evaluation/ml_classification.ipynb`

## Phase 5: User Story 2 - Comparative Visualization (P2)
Goal: Visualize the most discriminative phonemes.
Independent Test: Verify that 10 histograms are saved in the output directory.

- [x] T019 [US2] Implement effect size calculation (Cohen's d) to identify top 10 phonemes in `phoneme_evaluation/analyzer.py`
- [x] T020 [US2] Implement histogram generation logic in `phoneme_evaluation/visualizer.py`
- [x] T021 [US2] Create execution script `phoneme_evaluation/run_viz.py` to save plots to `reports/plots/phonemes/`

## Phase 6: Polish & Validation
Goal: Final cleanup and consistency check.

- [x] T022 [P] Add docstrings and type hints to all Python files in `phoneme_evaluation/`
- [x] T023 Verify classification results against `embeddings_eval` performance in `phoneme_evaluation/ml_classification.ipynb`
- [x] T024 Perform final run of all scripts to ensure reproducibility

## Implementation Strategy
- **MVP**: Complete Phase 1-3 to get initial statistics and verify the data pipeline.
- **Incremental**: Follow with Phase 4 (Classification) as it is the primary research goal.
- **Polish**: Phase 5 and 6 can be done once the core metrics are validated.

## Dependencies
- US1 (Stats) is a prerequisite for US2 (Viz) and US3 (Classification).
- Foundational tasks (Phase 2) block all User Stories.

## Parallel Opportunities
- T003 and T004 can be done simultaneously.
- T007 (Outlier detection) can be developed independently of T005 (Metadata).
- T015 (CV logic) can be prototyped in the notebook while the service layer is being finalized.
- T022 (Docstrings) can be done in parallel for any completed file.
