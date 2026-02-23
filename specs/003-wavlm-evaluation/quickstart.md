# Quickstart: wavLM-evaluation

Tools for hierarchical evaluation and machine learning classification of WavLM embeddings from the PC-GITA corpus.

## Installation
Ensure all dependencies are installed in your `.venv`:
```bash
pip install torch pandas scikit-learn matplotlib seaborn tqdm ipywidgets
```

## Running the Evaluation

### 1. Hierarchical Distance Tables
Browse distances between individual recordings and centroids:
- Open `embeddings_eval/report_tables.ipynb`
- Features interactive selection of speakers and Mean/Variance summaries.

### 2. Interactive Visualization (Spider Plots)
Visualize speaker clusters and task-group hierarchy:
- Open `embeddings_eval/interactive_eval.ipynb`
- Gender-aware coloring and hierarchy lines.

### 3. Machine Learning Analysis
Evaluate predictive power for Sex, Age, and PD status:
- Open `embeddings_eval/classification_analysis.ipynb`
- Uses **StratifiedGroupKFold (n=10)**.
- **Note**: DDK data is excluded from PD/HC detection to ensure a fair comparison with the HC group.
- **Aggregation**: Compare Majority Vote vs. Average Probability at the speaker level.

## Core Script
To generate raw CSV reports:
```bash
python -m embeddings_eval.run_eval
```
Reports are saved to the `reports/` directory.
