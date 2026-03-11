# dysarthric-TTS Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-02-25

## Active Technologies

- Python 3.11+ + librosa, pandas, soundfile, ruff, mypy, pytest, nbformat, nbconvert (001-segment-pcgita-sentences)

## Project Structure

```text
src/
tests/
```

## Commands

cd src; pytest; ruff check .

## Code Style

Python 3.11+: Follow standard conventions

## Recent Changes

- 006-dataset-comparison: Added `dataset_comparison` module for comparing reference (PC-GITA) and test (TTS) datasets. Features include data integrity (Wav, CSV, TXT, PT), transcription identity, 50% relative audio duration threshold, and WavLM embedding distances (Cosine & Euclidean). Includes an interactive English-localized Jupyter notebook for side-by-side audio comparison, global experiment summaries, and sentence-level fidelity vs. natural diversity baselines (Ref-Test vs Ref-Ref).
- 005-speaker-reference: Added `speaker_reference_6.py` with enhanced multi-tier fallback logic. Primary source is Sentence 6, with fallback to 3-4s segments with dots, and a final flexible fallback (2-6s) to ensure 100% speaker coverage.
- 004-phoneme-evaluation: Added phoneme duration analysis, Cohen's d effect size, Z-score outlier filtering, and speaker-level PD vs HC classification.
- 001-segment-pcgita-sentences: Added Python 3.11+ + librosa, pandas, soundfile, ruff, mypy, pytest, nbformat, nbconvert

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
