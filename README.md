# FAU dysarthric-TTS (PC-GITA)

Preprocessing and synthetic speech training for healthy vs dysarthric speakers using the PC-GITA dataset.

## Setup Instructions

This project uses a local Python virtual environment.

### 1. Create the environment
```powershell
python -m venv .venv
```

### 2. Activate the environment
- **Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- **Linux/macOS:**
  ```bash
  source .venv/bin/activate
  ```

### 3. Install dependencies
```bash
pip install -e .
# Or manually:
pip install librosa pandas soundfile pytest ruff mypy jupyter nbformat nbconvert matplotlib seaborn
```

## PC-GITA Sentence Splitting

Split recordings into sentences based on phoneme alignment:

```powershell
python data_prepare/split_sentences.py `
    --input_dir datalocal/v260210_24kHz/readtext `
    --output_dir datalocal/v260210_24kHz/readtext_split `
    --max_sentence_length 15.0 `
    --min_speech_duration 1.0 `
    --min_word_count 2
```

- **Core Logic**: 
  - Prioritizes keeping sentences together (Pause + Uppercase).
  - If a sentence > 15s, it breaks it up using **commas** (first) or **long pauses** (second).
  - Enforces minimum constraints (>= 2 words, >= 1s speech) via automatic merging.
- **New Features**:
  - **Silence Cropping**: `--max_silence_ms` clips leading/trailing silence.
  - **Duration Safety**: If cropping violates constraints, silence is reduced partially.
  - **Auto-Comma**: If a split happens mid-sentence, a comma is added.
  - **Internal Comma**: If a gap between words exceeds 250ms, a comma is inserted.
  - **Trailing Dot**: Transcripts automatically end with a period.
  - **Enhanced Logging**: Prints duration, speech info, and transcription text.

## Segment Merging

Concatenate short segments into larger units (~5 words):

```powershell
python data_prepare/merge_words.py `
    --input_dir datalocal/v260210_24kHz/readtext_split `
    --output_dir datalocal/v260210_24kHz/readtext_merged
```

- **Logic**: 
  - Targets 5 words per merged segment.
  - Ensures a minimum of 4 words (merges leftovers into previous groups).
  - Synchronizes WAV, TXT, and CSV (shifts alignment timings and offsets `TOKEN` IDs).
  - Transcripts are generated with a **dot after every word**.
- **Naming**: `[prefix]_[word1]_[word2]...` (e.g., `001PD_S1_el_medico_fue`).

## Dataset Analysis & Statistics

After segmentation, you can use the provided Jupyter notebook to validate the data and generate reports:

- **Notebook**: `data_prepare/split_sentences_stats.ipynb`
- **Capabilities**:
  - Triple validation (ensures every segment has matching `.wav`, `.txt`, and `.csv`).
  - Breakdown of word counts, sentence counts, and total duration for Healthy Control (HC) and Patient (PD) groups.
  - **Silence Analysis**: Computes and visualizes (via histograms) the distribution of leading and trailing silence across all segments.
  - Generates machine-readable reports in `reports/`.

## Alignment Checking

Interactively verify audio-to-text alignment:

- **Notebook**: `data_prepare/check_alignment.ipynb`
- **Capabilities**:
  - Filter by speaker and segment.
  - View waveform and spectrogram with overlaid phoneme/word boundaries.
  - Play audio segments directly in the browser.

## Monologue Transcription

For the monologue subset, use the following script to generate normalized transcripts from master metadata:

```powershell
python data_prepare/get_monologue_transcription.py
```

- **Inputs**: `datalocal/v260210_24kHz/_metadata/` (mapping and master text).
- **Outputs**: `.txt` files in `datalocal/v260210_24kHz/monologue/`.
- **Formatting**: Lowercase, sentence-start capitalization, punctuation spacing correction.

## Dataset Protection

**CRITICAL**: NEVER commit real PC-GITA audio, transcripts, or metadata to this repository. All raw data should be stored in `datalocal/` which is ignored by git.

The repository includes a minimal synthetic dummy dataset in `tests/data_prepare/dummy_data/` for CI and testing.
