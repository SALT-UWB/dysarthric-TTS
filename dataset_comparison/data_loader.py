import pandas as pd
import torch
from pathlib import Path
from typing import Optional
from .constants import METADATA_PATH

def load_metadata() -> pd.DataFrame:
    """
    Loads speaker metadata and categorizes by health status (PD/HC).
    """
    if not METADATA_PATH.exists():
        # Fallback for different environments
        fallback = Path("datalocal/PCGITAtoPD_mapping.csv")
        if fallback.exists():
            df = pd.read_csv(fallback, sep=';')
        else:
            raise FileNotFoundError(f"Metadata not found at {METADATA_PATH}")
    else:
        df = pd.read_csv(METADATA_PATH, sep=';')

    df = df[['Code BD-Parkinson', 'SEX', 'AGE', 'H/Y']].copy()
    df.columns = ['speaker_id', 'sex', 'age', 'hy']
    df['status'] = df['hy'].apply(lambda x: 'PD' if x > 0 else 'HC')
    return df

def load_embedding(path: Path) -> torch.Tensor:
    """
    Loads a WavLM embedding from a .pt file.
    """
    return torch.load(path, map_location='cpu', weights_only=True)
