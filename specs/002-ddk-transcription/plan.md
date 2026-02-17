# Implementation Plan - DDK Transcription

The goal is to generate normalized `.txt` transcripts for DDK recordings by mapping filenames to segment-based source metadata.

## User Review Required

> [!IMPORTANT]
> - Source filenames (e.g., `001PD`) are mapped to transcript IDs (e.g., `AVPE...`) via `PCGITAtoPD_mapping.csv`.
> - Transcript text is extracted from `DDK[1-3].txt` files which contain timestamped segments.
> - Comma insertion depends on temporal gaps (> 200ms) between segments.

## Proposed Changes

### `data_prepare/`

#### [NEW] `get_ddk_transcription.py`
- CLI tool to process DDK recordings.
- Parses segment-based DDK source files.
- Implements gap analysis and text normalization (lowercase, period, comma).

## Verification Plan

### Automated Tests
- Run script on a test subset and verify:
    - [ ] Mapping works correctly.
    - [ ] Comma is inserted only when gap > 200ms.
    - [ ] Lowercase conversion and trailing period.

### Manual Verification
- Inspect generated `.txt` files in `datalocal/v260210_24kHz/ddk/`.
- Check warnings in logs for missing data.
