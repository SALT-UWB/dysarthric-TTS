# Development Plan - wavLM-evaluation

Implementation of a comprehensive evaluation suite for WavLM embeddings extracted from PC-GITA.

## Phase 1: Data & Metadata (Completed)
- [x] Implement `data_loader.py` with Sex, Age, and H/Y mapping.
- [x] Refine group parsing (4-word pattern for `words` group).

## Phase 2: Hierarchical Logic (Completed)
- [x] Implement `analyzer.py` with DDK-exclusion for global centroids.
- [x] Add `classify_to_nearest_group` for speaker assignment analysis.

## Phase 3: Reporting & Visualization (Completed)
- [x] `reporter.py`: Add TOP 5 intruder detection and English labels.
- [x] `visualizer.py`: Spider-plot with connection lines and gender-aware colors.
- [x] `centroid_speaker_assignment.ipynb`: Consolidate non-ML hierarchical analysis.

## Phase 4: Machine Learning Suite (Completed)
- [x] `ml_classification_analysis.ipynb`: 
    - Sex Classification: LR, MLP, HGBT.
    - Age Prediction: Ridge, HGBT + Distribution & Error Histograms.
    - PD/HC Detection: LR, MLP, HGBT (Excluding DDK recordings).
    - Summary Evaluation: Compare Sample Acc, Maj. Vote (Conf), and Avg. Prob (Prob) across all subsets (All, Monologue, Readtext, Sentence, Words, Monologue+Sentence).
    - Styled Summaries: Green (All correct), Red (Overall wrong), Orange (Group mismatch).
    - Progress Tracking: Integrated `tqdm` for all training loops.
- [x] Robust validation using StratifiedGroupKFold (n=10).
