# Spec 005: Speaker Reference Generation

## Goal
Generate a consistent reference audio file for every speaker in the PC-GITA dataset (100 speakers total) to serve as a baseline for acoustic and embedding comparisons.

## Background
Different speakers have different levels of data availability. While most have cleaned sentences (Sentences 5 and 6 are standard), some speakers were excluded from the cleaned set due to segmentation issues or missing files. To ensure 100% coverage, a fallback mechanism is required to pull audio from other tasks (Readtext or Monologue).

## Requirements
- **Input Sources**:
  - Primary: `datalocal/PC-GITA_v260210_24kHz/sentences_cleaned`
  - Fallback 1: `datalocal/PC-GITA_v260210_24kHz/readtext_split`
  - Fallback 2: `datalocal/PC-GITA_v260210_24kHz/monologue_split`
- **Output**:
  - Directory: `datalocal/PC-GITA_v260210_24kHz/speakers_ref_sentences/`
  - Format: Triplets of `.wav`, `.txt`, and `.csv` (alignment).
- **Selection Logic**:
  1. If Sentence 5 AND Sentence 6 exist in `sentences_cleaned`, merge all their segments.
  2. Else, if segments exist in `readtext_split`, concatenate segments until 6.0 - 8.0 seconds of audio is reached.
  3. Else, use `monologue_split` segments to reach the 6.0 - 8.0 second target.
- **Data Integrity**:
  - Shift CSV alignment timings (`BEGIN`) when concatenating segments.
  - Offset `TOKEN` IDs in CSV to maintain uniqueness across concatenated segments.
  - Merge `.txt` transcripts with appropriate spacing.

## Naming Convention
- **Sentences**: `{speaker_id}_{session}_sentences_5_6`
- **Fallbacks**: `{speaker_id}_{session}_{task}_{segment_ids}` (e.g., `005PD_S1_readtext_001_002_003`)
