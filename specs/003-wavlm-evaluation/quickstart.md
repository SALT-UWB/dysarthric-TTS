# Quickstart: wavLM-evaluation

Tools for hierarchical evaluation and machine learning classification of WavLM embeddings from the PC-GITA corpus.

## Installation
Ensure all dependencies are installed in your `.venv`:
```bash
pip install torch pandas scikit-learn matplotlib seaborn tqdm ipywidgets
```

## Available Notebooks

### 1. Statistical Tables & Spider Plots (`embeddings_eval/centroid_speaker_assignment.ipynb`)
Comprehensive suite for non-ML evaluation:
- **Speaker Assignment**: Identifies success in mapping files to correct centroids (with Top 5 intruders).
- **Distance Tables**: Interactive browsing of Mean/Variance distance metrics for all task groups.
- **Visual Exploration**: Global centroid maps and interactive **Spider Plots** showing hierarchical connections (Sample -> Group -> Speaker).

### 2. ML Classification Analysis (`embeddings_eval/ml_classification_analysis.ipynb`)
Comprehensive ML evaluation suite:
- **Experiments**: Sex, Age, and PD status prediction across multiple model architectures.
- **Summary Metrics**: Sample Accuracy, Majority Vote (with Confidence), and Average Probability (with Prob score).
- **Subsets**: All data, individual task groups, and combined `monologue+sentence`.
- **Note**: DDK data is excluded from PD/HC detection to ensure a fair comparison.
- **Progress Tracking**: Real-time feedback via `tqdm` progress bars.

## Core Script
To generate raw CSV reports for all speakers:
```bash
python -m embeddings_eval.run_eval
```
Output files will be generated in the `reports/` directory.
