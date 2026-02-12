# Quickstart: segment-pcgita-sentences

## Environment Setup

1. Create the virtual environment:
   ```powershell
   python -m venv .venv
   ```

2. Activate the environment:
   - Windows: `.venv\Scripts\Activate.ps1`
   - Linux/macOS: `source .venv/bin/activate`

3. Install dependencies:
   ```bash
   pip install librosa pandas soundfile pytest ruff mypy jupyter
   ```

## Running the Splitting Script

```bash
python data_prepare/split_sentences.py --input_dir datalocal/PC_GITA/v260210_24kHz/readtext --output_dir datalocal/processed/v1
```

**Expected Output:**
```text
2026-02-12 15:15:01,123 - data_prepare.split_sentences - INFO - Found 100 WAV files in datalocal/PC_GITA/v260210_24kHz/readtext
2026-02-12 15:15:02,456 - data_prepare.split_sentences - INFO - Processed 001PD_S1_readtext: generated 5 segments
...
2026-02-12 15:16:45,789 - data_prepare.split_sentences - INFO - 
--- Run Summary ---
2026-02-12 15:16:45,790 - data_prepare.split_sentences - INFO - Total source files processed: 100
2026-02-12 15:16:45,791 - data_prepare.split_sentences - INFO - Total segments generated: 512
```

## Running the Validation Notebook

1. Launch Jupyter:
   ```bash
   jupyter notebook
   ```
2. Open `data_prepare/split_sentences.ipynb`.
3. Set the `DATA_DIR` variable to your output path (e.g., `../datalocal/processed/v1`).
4. Run all cells to generate the stats report in `reports/dataset_stats.json`.
