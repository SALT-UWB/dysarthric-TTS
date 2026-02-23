# Quickstart: wavLM-evaluation

Tools for hierarchical evaluation and machine learning classification of WavLM embeddings from the PC-GITA corpus.

## Installation
Ensure all dependencies are installed in your `.venv`:
```bash
pip install torch pandas scikit-learn matplotlib seaborn tqdm ipywidgets
```

## Available Notebooks

### 1. Statistical Tables (`embeddings_eval/report_tables.ipynb`)
Browse numerical distances between individual recordings and centroids:
- Features interactive selection of speakers.
- Summary Mean/Variance tables for both PD and HC groups.

### 2. Interactive Visualization (`embeddings_eval/interactive_eval.ipynb`)
Visual exploration of embedding clusters:
- **Spider Plots**: Connect individual samples to their group centroids and group centroids to the speaker global mean.
- **Color Coding**: Status and Gender aware (Red/Purple for PD, Green/Light Green for HC).

### 3. Classification Analysis (`embeddings_eval/classification_analysis.ipynb`)
Comprehensive ML evaluation suite:
- **Sex Classification**: Evaluating LR, MLP, and HGBT.
- **Age Prediction**: Visualizing distribution and prediction error (Ridge, HGBT).
- **PD/HC Detection**: Advanced aggregation (Majority Vote / Avg Proba) with H/Y severity context.
- **Progress Tracking**: Real-time feedback via `tqdm` progress bars.

## Core Script
To generate raw CSV reports for all speakers:
```bash
python -m embeddings_eval.run_eval
```
Output files will be generated in the `reports/` directory.
