import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Optional
from .constants import METADATA_PATH, DATA_ROOT, TASKS, SAMPLING_RATE
from .utils import extract_speaker_id

def load_metadata() -> pd.DataFrame:
    """
    Loads speaker metadata from the mapping CSV.
    HC: H/Y == 0, PD: H/Y > 0
    """
    if not METADATA_PATH.exists():
        # Try local path if absolute path fails
        local_metadata = Path("datalocal/PC-GITA_v260210_24kHz/_metadata/PCGITAtoPD_mapping.csv")
        if local_metadata.exists():
            df = pd.read_csv(local_metadata, sep=';')
        else:
            raise FileNotFoundError(f"Metadata not found at {METADATA_PATH}")
    else:
        df = pd.read_csv(METADATA_PATH, sep=';')
        
    # Filter and rename for clarity
    df = df[['Code BD-Parkinson', 'SEX', 'AGE', 'H/Y']].copy()
    df.columns = ['speaker_id', 'sex', 'age', 'hy']
    df['status'] = df['hy'].apply(lambda x: 'PD' if x > 0 else 'HC')
    return df

def parse_alignment(file_path: Path, task: str) -> pd.DataFrame:
    """
    Parses a single webMAUS alignment CSV.
    Converts BEGIN and DURATION from samples to seconds.
    """
    try:
        df = pd.read_csv(file_path, sep=';')
        
        # Check required columns
        if not all(col in df.columns for col in ['MAU', 'BEGIN', 'DURATION']):
            return pd.DataFrame()
            
        df = df[['BEGIN', 'DURATION', 'MAU']].copy()
        df.columns = ['begin', 'duration_samples', 'phoneme']
        
        # Convert to seconds
        df['duration'] = df['duration_samples'] / SAMPLING_RATE
        df['begin_sec'] = df['begin'] / SAMPLING_RATE
        
        # Add metadata context
        df['speaker_id'] = extract_speaker_id(file_path)
        df['task'] = task
        df['file_stem'] = file_path.stem
        
        return df
    except Exception as e:
        # print(f"Error parsing {file_path}: {e}")
        return pd.DataFrame()

def filter_outliers(df: pd.DataFrame, z_threshold: float = 3.0) -> pd.DataFrame:
    """
    Removes outliers based on phoneme duration.
    Calculates Z-score per phoneme type.
    """
    if df.empty:
        return df
        
    filtered_dfs = []
    for phoneme, group in df.groupby('phoneme'):
        if len(group) < 5:
            filtered_dfs.append(group)
            continue
            
        mean = group['duration'].mean()
        std = group['duration'].std()
        
        if std == 0:
            filtered_dfs.append(group)
            continue
            
        z_scores = (group['duration'] - mean) / std
        filtered_group = group[np.abs(z_scores) < z_threshold]
        filtered_dfs.append(filtered_group)
        
    return pd.concat(filtered_dfs, ignore_index=True)

def load_all_data(tasks: List[str] = TASKS, z_threshold: Optional[float] = 3.0, filter_technical: bool = True) -> pd.DataFrame:
    """
    Loads alignments from all specified directories, merges with metadata, and filters outliers.
    Set filter_technical=False to keep <p:>, <usb>, etc. (e.g., for visualization).
    """
    from .constants import TECHNICAL_TOKENS
    
    print(f"Loading metadata from {METADATA_PATH}...")
    metadata = load_metadata()
    all_alignments = []
    
    print(f"Processing directories: {tasks}")
    
    for task in tasks:
        task_dir = DATA_ROOT / task
        if not task_dir.exists():
            print(f" - Warning: Directory {task_dir} not found.")
            continue
            
        # Search for CSV files in root and in common subfolders like ali_phoneme
        files = list(task_dir.glob("*.csv")) + list(task_dir.glob("ali_phoneme/*.csv"))
        
        if not files:
            print(f" - No CSV files found in {task}")
            continue
            
        print(f" - Found {len(files)} files in {task}")
        for f in files:
            df_align = parse_alignment(f, task)
            if not df_align.empty:
                all_alignments.append(df_align)
                
    if not all_alignments:
        print("No alignment data loaded!")
        return pd.DataFrame()
        
    df_all = pd.concat(all_alignments, ignore_index=True)
    
    # Filter technical tokens before merging/outlier detection
    if filter_technical:
        print(f"Filtering technical tokens: {TECHNICAL_TOKENS}")
        df_all = df_all[~df_all['phoneme'].isin(TECHNICAL_TOKENS)]
    
    # Merge with metadata
    df_merged = df_all.merge(metadata, on='speaker_id', how='left')
    
    # Filter outliers
    if z_threshold is not None:
        print(f"Filtering outliers with Z-threshold={z_threshold}...")
        df_merged = filter_outliers(df_merged, z_threshold)
        
    print(f"Total samples loaded: {len(df_merged)}")
    return df_merged

def get_speaker_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Constructs a feature vector for each speaker.
    Features include mean and variance of duration for each phoneme.
    """
    # Group by speaker and phoneme
    speaker_phoneme_stats = df.groupby(['speaker_id', 'status', 'sex', 'phoneme'])['duration'].agg(['mean', 'var']).reset_index()
    
    # Pivot to get one row per speaker
    features_pivot = speaker_phoneme_stats.pivot(index='speaker_id', columns='phoneme', values=['mean', 'var'])
    
    # Flatten columns: ('mean', 'a') -> 'mean_a'
    features_pivot.columns = [f"{stat}_{ph}" for stat, ph in features_pivot.columns]
    
    # Join back with speaker metadata (status, sex)
    metadata = speaker_phoneme_stats[['speaker_id', 'status', 'sex']].drop_duplicates().set_index('speaker_id')
    feature_df = metadata.join(features_pivot)
    
    # Handle missing values
    feature_df = feature_df.fillna(0)
    
    return feature_df
