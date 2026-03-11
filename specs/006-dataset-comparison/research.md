# Research: Dataset Comparison

## Technical Context & Unknowns

- **Embedding Format**: Confirmed as PyTorch `.pt` files.
- **Phoneme Alignment**: CSV format with semicolons (`BEGIN;DURATION;TOKEN;MAU;ORT`).
- **Parallelism**: Comparison is based on matching filenames across task directories.
- **Metadata**: Health status (PD/HC) and Sex are derived from speaker ID using `PCGITAtoPD_mapping.csv`.

## Research Findings

### Decision 1: Dual Embedding Distance Metrics
- **Choice**: **Cosine Distance** and **Euclidean Distance**.
- **Rationale**: Cosine measures directional (identity/phonetic) similarity regardless of volume. Euclidean captures absolute acoustic fidelity. Providing both ensures a comprehensive evaluation.

### Decision 5: Baseline Normalization
- **Choice**: **Inter-speaker diversity (Ref-Ref)**.
- **Rationale**: Establishing how much natural speakers differ for the same sentence provides a context for "closeness." Synthesis is successful if Ref-Test distance is significantly smaller than the natural Ref-Ref variation.

### Decision 2: Phoneme Comparison Logic
- **Choice**: Duration difference ($\Delta t = |t_{ref} - t_{test}|$) and Presence check.
- **Rationale**: Direct subtraction of duration for aligned phonemes is the standard for TTS temporal fidelity evaluation.
- **Edge Cases**: If a phoneme is missing in test, mark as "Missing" and exclude from average duration delta calculation.

### Decision 3: Audio Duration Threshold
- **Choice**: 50ms tolerance.
- **Rationale**: Minor differences in silence or padding are expected in TTS, but differences >50ms often indicate skipped words or elongated vowels.

### Decision 4: Grouping Strategy
- **Choice**: Tiered aggregation (Sample -> Speaker -> Group (PD/HC)).
- **Rationale**: Aligns with existing analysis in `embeddings_eval` and `phoneme_evaluation`.
