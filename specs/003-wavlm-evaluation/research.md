# Research: wavLM-evaluation

## Metadata Integration
- **H/Y Scale**: Hoehn & Yahr scores correlate misclassifications with disease severity.
- **DDK Bias Mitigation**: Diadochokinetic (DDK) task is excluded from PD/HC classification to prevent trivial features (as HC lacks DDK) from inflating accuracy.

## Evaluation Methodology
- **Speaker Assignment**: A nearest-centroid approach evaluates acoustic identity uniqueness.
- **Validation**: StratifiedGroupKFold (n=10) ensures balanced status distribution while strictly avoiding speaker leakage.
- **Aggregation Logic**:
    - **Majority Vote**: Final label based on the most frequent prediction in a group.
    - **Average Probability**: Final label based on the mean softmax output; score in parentheses indicates model confidence.

## Visualization Strategy
- **Spider Plots**: Shows hierarchy (Sample -> Group -> Speaker).
- **Histograms**: Visualizes Age Distribution and MAE residuals.
- **Styled Dataframes**: Uses conditional formatting to highlight success (Green), global failure (Red), and task-specific inconsistencies (Orange).

## Machine Learning Models
- **Logistic Regression (LR) / Ridge**: Baseline performance.
- **MLP (256, 128, 64)**: Non-linear feature extraction.
- **HistGradientBoosting (HGBT)**: High-performance gradient boosting for tabular embedding data.
