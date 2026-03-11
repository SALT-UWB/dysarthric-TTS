# Quickstart: Dataset Comparison

## Setup
1. Ensure both reference and test datasets are located in `datalocal/` (or specify absolute paths).
2. Verify WavLM embeddings (.pt) have been pre-calculated and stored in `{corpus_root}/speaker_embeddings/wavLM`.
3. Metadata `PCGITAtoPD_mapping.csv` must exist in `datalocal/PC-GITA_v260210_24kHz/_metadata/`.

## Execution
Run the comparison module from the project root:
```bash
python -m dataset_comparison.run_comparison --ref datalocal/PC-GITA_v260210_24kHz --test datalocal/genPC-GITA_ZipVoice-CML-CV_ref-CML-wavLM
```

## Visualization
Launch the Jupyter notebooks:
- **Audio Integrity**: `jupyter notebook dataset_comparison/dataset_comparison_viz.ipynb`
- **Embedding Analysis**: `jupyter notebook dataset_comparison/embedding_comparison_viz.ipynb`

In `embedding_comparison_viz.ipynb`, you can:
- View a **Global Overview** comparing all models in the `reports/` folder.
- Analyze **Fidelity vs. Natural Diversity** (Ref-Test vs. Ref-Ref) for sentences 1-10.
- Compare Cosine and Euclidean distances side-by-side.

## Outputs
Reports are saved in `reports/comparison_{ref}_{test}/`:
- `comparison_integrity.csv`: Missing files and transcription mismatches.
- `comparison_audio_durations.csv`: Duration deltas and significance flags (>50% difference).
- `speaker_embedding_summary.csv`: Aggregated distances per speaker/task.
- `comparison_phonemes.csv`: Phoneme-level duration deltas and missing token flags.
