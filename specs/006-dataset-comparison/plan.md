# Implementation Plan: Dataset Comparison

## Technical Context
- **Language**: Python 3.11+
- **Key Libraries**: `pandas`, `numpy`, `scipy` (distance), `torch` (load embeddings), `librosa` (audio duration).
- **Architecture**: Modular scripts for data loading, metric calculation, and reporting.

## Phases

### Phase 1: Data Integrity & Audio Metrics
- Implement `DataIntegrityChecker` to walk directories and compare file lists.
- Check `.txt` transcription identity.
- Calculate audio durations using `soundfile` or `librosa`.

### Phase 2: Embedding Comparison
- Implement `EmbeddingComparator`.
- Load `.pt` files, calculate Cosine distance.
- Aggregate by speaker and group.

### Phase 3: Phoneme Comparison
- Implement `PhonemeComparator`.
- Parse semicolon-separated CSVs.
- Calculate duration deltas and identify missing phonemes.

### Phase 4: Visualization & Reporting
- Export CSV summaries to `reports/`.
- Develop `dataset_comparison_viz.ipynb` with `matplotlib`/`seaborn`.
- Distinguish PD vs HC in all plots.

## Constitution Check
- No hardcoded paths: Use CLI arguments.
- Reproducibility: Save all intermediate metrics to CSV.
- Consistency: Use same grouping logic as `embeddings_eval`.
