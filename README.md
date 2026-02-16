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
    --max_silence_ms 500
```

- **Core Logic**: Splits at midpoints of pauses (`<p:>`) if followed by a capital letter or if the pause exceeds `--pause_threshold`.
- **New Features**:
  - **Silence Cropping**: `--max_silence_ms` clips leading/trailing silence (WAV and CSV synced).
  - **Duration Safety**: If cropping violates `--min_duration`, silence is reduced **partially** (proportionally) to maintain the minimum length.
  - **Auto-Comma**: If a split happens mid-sentence, a comma is added to the TXT output.
  - **Punctuation**: Preserves punctuation from source TXT files via `TOKEN` mapping.

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
