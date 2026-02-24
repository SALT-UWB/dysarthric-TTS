import pandas as pd
from pathlib import Path
from typing import List
from .analyzer import calculate_stats

def generate_full_report(df: pd.DataFrame, output_path: Path):
    """
    Generates a long-form report with all splits.
    """
    reports = []
    
    # 1. Total statistics
    total_stats = calculate_stats(df, [])
    total_stats['split'] = 'Total'
    reports.append(total_stats)
    
    # 2. Status split
    status_stats = calculate_stats(df, ['status'])
    status_stats['split'] = 'Status'
    reports.append(status_stats)
    
    # 3. Status + Sex split
    status_sex_stats = calculate_stats(df, ['status', 'sex'])
    status_sex_stats['split'] = 'Status+Sex'
    reports.append(status_sex_stats)
    
    final_cols = ['split', 'task', 'status', 'sex', 'phoneme', 'mean_duration', 'var_duration', 'sample_count']
    combined_report = []
    for r in reports:
        for col in final_cols:
            if col not in r.columns:
                r[col] = 'All'
        combined_report.append(r[final_cols])
        
    final_df = pd.concat(combined_report, ignore_index=True)
    final_df.to_csv(output_path, index=False)
    return final_df

def generate_wide_report(df: pd.DataFrame, output_path: Path):
    """
    Generates a wide-form report specifically requested by the user.
    Columns: All, PD (Total, M, F), HC (Total, M, F)
    Values: Mean and Var
    """
    # Define groups for columns
    configs = [
        {'name': 'All', 'filter': {}},
        {'name': 'PD', 'filter': {'status': 'PD'}},
        {'name': 'PD_M', 'filter': {'status': 'PD', 'sex': 'M'}},
        {'name': 'PD_F', 'filter': {'status': 'PD', 'sex': 'F'}},
        {'name': 'HC', 'filter': { 'status': 'HC'}},
        {'name': 'HC_M', 'filter': {'status': 'HC', 'sex': 'M'}},
        {'name': 'HC_F', 'filter': {'status': 'HC', 'sex': 'F'}},
    ]
    
    final_results = []
    
    for config in configs:
        temp_df = df.copy()
        for col, val in config['filter'].items():
            temp_df = temp_df[temp_df[col] == val]
            
        if temp_df.empty:
            continue
            
        # Group only by phoneme
        stats = temp_df.groupby('phoneme')['duration'].agg(['mean', 'var', 'count']).reset_index()
        # Rename columns with prefix
        prefix = config['name']
        stats.columns = ['phoneme', f'{prefix}_mean', f'{prefix}_var', f'{prefix}_count']
        
        if len(final_results) == 0:
            final_results.append(stats)
        else:
            final_results.append(stats.set_index('phoneme'))
            
    # Merge all
    wide_df = final_results[0].set_index('phoneme')
    for other_df in final_results[1:]:
        wide_df = wide_df.join(other_df, how='outer')
        
    wide_df = wide_df.reset_index()
    
    # Save to CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wide_df.to_csv(output_path, index=False)
    print(f"Wide report saved to {output_path}")
    
    return wide_df
