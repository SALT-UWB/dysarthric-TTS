import pandas as pd
import numpy as np
from typing import Dict, List

def calculate_stats(df: pd.DataFrame, groupby_cols: List[str]) -> pd.DataFrame:
    """
    Calculates mean and variance of duration for each phoneme within specified groups.
    """
    stats = df.groupby(groupby_cols + ['phoneme'])['duration'].agg(['mean', 'var', 'count']).reset_index()
    stats.columns = groupby_cols + ['phoneme', 'mean_duration', 'var_duration', 'sample_count']
    return stats

def get_phoneme_diff_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates differences and Cohen's d for all phonemes between PD and HC.
    Returns a DataFrame sorted by Cohen's d (descending).
    """
    hc_data = df[df['status'] == 'HC']
    pd_data = df[df['status'] == 'PD']
    
    phonemes = df['phoneme'].unique()
    differences = []
    
    for ph in phonemes:
        h = hc_data[hc_data['phoneme'] == ph]['duration']
        p = pd_data[pd_data['phoneme'] == ph]['duration']
        
        if len(h) < 5 or len(p) < 5:
            continue
            
        mean_h, mean_p = h.mean(), p.mean()
        mean_diff = mean_p - mean_h # Positive if PD is slower
        
        s_h, s_p = h.std(), p.std()
        n_h, n_p = len(h), len(p)
        
        if s_h == 0 and s_p == 0:
            d = 0
        else:
            pooled_std = np.sqrt(((n_h - 1) * s_h**2 + (n_p - 1) * s_p**2) / (n_h + n_p - 2))
            d = mean_diff / pooled_std if pooled_std > 0 else 0
            
        differences.append({
            'phoneme': ph, 
            'mean_hc': mean_h, 
            'mean_pd': mean_p, 
            'diff': mean_diff, 
            'cohens_d': d,
            'abs_cohens_d': np.abs(d)
        })
        
    diff_df = pd.DataFrame(differences)
    if diff_df.empty:
        return pd.DataFrame()
        
    return diff_df.sort_values(by='abs_cohens_d', ascending=False)

def get_discriminative_phonemes(df: pd.DataFrame, top_n: int = 10) -> List[str]:
    """
    Returns a list of the top N phonemes sorted by absolute Cohen's d.
    """
    diff_df = get_phoneme_diff_stats(df)
    if diff_df.empty:
        return []
    return diff_df.head(top_n)['phoneme'].tolist()
