# Quickstart: Phoneme Evaluation

Follow these steps to run the phoneme-based analysis and classification.

## Prerequisites
- Python 3.11+
- Local virtual environment `.venv` with project dependencies.

## Running the Analysis
1. **Compute Statistics**:
   ```powershell
   .venv\Scripts\python.exe -m phoneme_evaluation.run_stats
   ```
   Generates `reports/phoneme_stats_wide.csv` (stratified by status and sex).

2. **Generate Plots**:
   ```powershell
   .venv\Scripts\python.exe -m phoneme_evaluation.run_viz
   ```
   Generates task-specific and global boxplots in `reports/plots/`.

3. **Open Notebooks**:
   - `phoneme_evaluation/statistics_visualization.ipynb`: Explains Cohen's d and shows interactive histograms.
   - `phoneme_evaluation/ml_classification.ipynb`: Runs speaker-level PD vs HC classification (with/without Sex feature) and shows the per-speaker results table.

## Key Methodology
- **Standardized Scale**: All duration boxplots use a fixed Y-axis from 0 to 0.25 seconds.
- **Biomarker Identification**: Phonemes are ranked by Cohen's d to highlight those with the highest discriminative power.
- **Aggregation**: Multiple recordings per speaker are aggregated into a single feature vector for robust classification.
