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

- 005-speaker-reference: Added `speaker_reference.py` with multi-source tiered logic (Sentences -> Readtext -> Monologue) to generate reference audio for all 100 speakers.
- 004-phoneme-evaluation: Added phoneme duration analysis, Cohen's d effect size, Z-score outlier filtering, and speaker-level PD vs HC classification.
- 001-segment-pcgita-sentences: Added Python 3.11+ + librosa, pandas, soundfile, ruff, mypy, pytest, nbformat, nbconvert

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
