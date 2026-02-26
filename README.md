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
    --max_sentence_length 10.0 `
    --min_speech_duration 1.0 `
    --min_word_count 2
```

- **Core Logic**: 
  - Prioritizes keeping sentences together (Pause + Uppercase).
  - If a sentence > 10s, it breaks it up using **commas** (first) or **long pauses** (second).
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
- **Naming**: `[prefix]_[word1]_[word2]...` (e.g., `001PD_S1_el_medico_fue`). Filenames are normalized to **ASCII** (accents removed) for filesystem compatibility, while `.txt` and `.csv` contents preserve original Spanish characters.

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

## DDK Transcription

Generate transcripts for DDK recordings with syllable-level gap analysis:

```powershell
python data_prepare/get_ddk_transcription.py
```

- **Logic**:
  - Maps speaker IDs (e.g., `001PD`) to transcript IDs via mapping CSV.
  - Inserts commas if the gap between syllable segments > threshold.
  - Normalizes to lowercase and adds a trailing period.
- **Arguments**:
  - `--pause_threshold_ms`: Gap threshold in ms to insert a comma (default: 300.0).
  - `--no_lowercase`: Disable lowercase conversion.
- **Inputs**: `datalocal/v260210_24kHz/ddk/` and `_metadata/DDK[1-3].txt`.

## Speaker Reference Generation

Generate high-quality reference audio for each speaker using a tiered source strategy:

```powershell
python data_prepare/speaker_reference.py
```

- **Logic**:
  - **Tier 1 (Primary)**: Uses Sentences 5 and 6 from `sentences_cleaned`. Concatenates all available segments for these sentences.
  - **Tier 2 (Fallback)**: If sentences are missing, uses the first segments from `readtext_split` to reach a target of 6-8 seconds of speech.
  - **Tier 3 (Final Fallback)**: Uses `monologue_split` segments to reach the 6-8 second target.
- **Naming Convention**:
  - Primary: `{speaker}_sentences_5_6`
  - Fallbacks: `{speaker}_{segment_ids}` (e.g., `005PD_S1_readtext_1_001_002_003`)
- **Output**: Saved in `datalocal/PC-GITA_v260210_24kHz/speakers_ref_sentences/`.

### Single Sentence Speaker Reference (`speaker_reference_6.py`)

A specialized version focused on a single representative sentence (primarily Sentence 6):

```powershell
python data_prepare/speaker_reference_6.py
```

- **Logic**:
  - **Tier 1**: Uses **Sentence 6** from `sentences_cleaned`.
  - **Tier 2/3**: Fallback to a single **3.0-4.0s** segment from `readtext_split` or `monologue_split` ending with a **dot**.
  - **Tier 4/5**: Flexible fallback to **2.0-6.0s** segments (no dot required).
  - **Tier 6**: Absolute fallback to **any** available segment to ensure 100% speaker coverage.
- **Output**: Saved in `datalocal/PC-GITA_v260210_24kHz/speakers_ref_sentence6/`.

## Phoneme Duration Evaluation

Analyze acoustic differences between PD and HC speakers based on phoneme alignment durations:

- **Core Analysis**:
  - Calculates mean and variance per phoneme, stratified by Status (PD/HC), Sex (M/F), and Task Group.
  - Identifies discriminative phonemes using **Cohen's d** effect size.
  - Filters technical alignment errors using **Z-score outlier detection (Z=3)**.
- **Machine Learning**:
  - Classifies speakers as PD or HC using **speaker-level** feature vectors (aggregated statistics).
  - Evaluates performance both with and without **Sex** as an additional feature.
  - Generates detailed **Per-Speaker Summaries** with colored result tables and classification probabilities.
- **Execution**:
  ```powershell
  .venv\Scripts\python.exe -m phoneme_evaluation.run_stats
  .venv\Scripts\python.exe -m phoneme_evaluation.run_viz
  ```
- **Notebooks**:
  - `phoneme_evaluation/statistics_visualization.ipynb`: Interactive exploration and stratified boxplots.
  - `phoneme_evaluation/ml_classification.ipynb`: Speaker-level classification experiments and per-individual results.

## Dataset Comparison

Evaluate synthetic parallel datasets (e.g., PC-GITA vs. TTS generated versions) to ensure fidelity and integrity:

- **Orchestration**:
  ```powershell
  python -m dataset_comparison.run_comparison `
      --ref datalocal/PC-GITA_v260210_24kHz `
      --test datalocal/genPC-GITA_ZipVoice-CML-CV_ref-CML-wavLM
  ```
- **Fidelity Metrics**:
  - **Data Integrity**: Verifies existence of parallel `.wav`, `.csv` (alignment), and `.txt` files.
  - **Transcription Content**: Checks if `.txt` files are identical and logs mismatches.
  - **Duration Delta**: Alerts on audio duration differences > 50% relative to the reference.
  - **WavLM Embeddings**: Calculates **Cosine Distances** between high-dimensional embeddings.
  - **Phoneme Fidelity**: Computes duration deltas per phoneme and identifies missing tokens in the test set.
- **Visualization**:
  - **Notebook**: `dataset_comparison/dataset_comparison_viz.ipynb`
  - **Interactive Analysis**:
    - Summary tables of embedding distances and variances across all task groups (DDK, monologue, readtext, sentences, words).
    - Group-level comparison (PD vs. HC) with H/Y severity scores integrated.
    - **Interactive Drill-down**: Select a problematic file from a dropdown to see side-by-side **transcripts**, **spectrograms**, and use **integrated audio players** for direct comparison.

## Dataset Protection
**CRITICAL**: NEVER commit real PC-GITA audio, transcripts, or metadata to this repository. All raw data should be stored in `datalocal/` which is ignored by git.

The repository includes a minimal synthetic dummy dataset in `tests/data_prepare/dummy_data/` for CI and testing.
