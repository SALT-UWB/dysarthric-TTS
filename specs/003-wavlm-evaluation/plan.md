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
- [x] `report_tables.ipynb`: Interactive browsing of distance metrics.

## Phase 4: Machine Learning Suite (Completed)
- [x] `classification_analysis.ipynb`: 
    - Sex Classification: LR, MLP, HGBT + Detailed breakdown.
    - Age Prediction: Ridge, HGBT + Distribution & Error Histograms.
    - PD/HC Detection: LR, MLP, HGBT (Excluding DDK recordings).
    - Aggregated Analysis: Majority Vote and Average Probability (LR, HGBT).
    - Styled Summaries: Green (All correct), Red (Overall wrong), Orange (Group mismatch).
    - Progress Tracking: Integrated `tqdm` progress bars for all training loops.
- [x] Robust validation using StratifiedGroupKFold (n=10).
