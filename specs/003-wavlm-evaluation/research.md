# Research: wavLM-evaluation

## Metadata Integration
- **H/Y Scale**: Hoehn & Yahr scores are included to correlate misclassifications with disease severity in PD/HC detection reports.
- **DDK Bias Mitigation**: The Diadochokinetic (DDK) task is strictly excluded from PD/HC classification models. Since the Healthy Control (HC) group lacks these recordings, including them would allow models to "cheat" by detecting the presence of the task rather than acoustic dysarthric features.

## Evaluation Methodology
- **Speaker Assignment**: A nearest-centroid approach evaluates acoustic identity uniqueness across task groups.
- **Validation Strategy**: StratifiedGroupKFold (n=10) is used to maintain health status balance while ensuring no individual speaker's files overlap between training and testing sets.
- **Aggregation Logic**:
    - **Majority Vote**: Final label based on the most frequent file-level prediction.
    - **Average Probability**: Final label based on the mean softmax output across a speaker's task group. Score in parentheses represents model confidence [0.0 - 1.0].

## Visualization & Display
- **Spider Plots**: Visualizes variance within a speaker's task groups relative to their global mean.
- **Histograms**: Verifies age demographics and ensures error distribution symmetry in regression tasks.
- **Styled Dataframes**: Conditional formatting highlights overall classification success (Green), global failures (Red), and task-specific inconsistencies (Orange).

## Machine Learning Models
- **Logistic Regression (LR) / Ridge**: Baseline performance benchmarks.
- **MLP (256, 128, 64)**: Captures complex non-linear acoustic signatures.
- **HistGradientBoosting (HGBT)**: High-performance gradient boosting optimized for large embedding vectors.
