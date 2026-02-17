# Feature Specification: ddk-transcription

**Feature Branch**: `002-ddk-transcription`

## User Story

As a researcher, I want to automatically generate transcripts for DDK (Diadochokinetic) recordings by mapping them to segment-based metadata, so that I have synchronized text for syllable-based speech analysis.

## Acceptance Criteria

1. **Given** a DDK WAV file (e.g., `001PD_S1_DDK1.wav`), **When** the script looks up the mapping, **Then** it MUST find the corresponding transcript in `DDK1.txt`.
2. **Given** segment timings in the source TXT, **When** the gap between segments is > 200ms, **Then** a comma MUST be inserted between the words.
3. **Given** the `--lowercase` flag, **When** generating text, **Then** all words MUST be converted to lowercase.
4. **Given** a generated transcript, **When** finalized, **Then** it MUST end with a period.
5. **Given** a missing mapping or transcript, **When** processing, **Then** a warning MUST be printed.

## Functional Requirements

- **FR-001**: System MUST parse `PCGITAtoPD_mapping.csv` to link `Code BD-Parkinson` to `CODE`.
- **FR-002**: System MUST parse segment-based DDK source files (DDK1.txt, DDK2.txt, DDK3.txt).
- **FR-003**: System MUST calculate gaps between segments (Start of current - End of previous).
- **FR-004**: System MUST provide a CLI with options for input directory and text normalization.
