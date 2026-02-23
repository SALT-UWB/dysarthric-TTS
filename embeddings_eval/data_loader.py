import os
import glob
import pandas as pd
from dataclasses import dataclass
from typing import List, Optional, Dict
import torch
from .constants import STATUS_PD, STATUS_HC, GROUP_WORDS, ALL_GROUPS, SEX_M

@dataclass
class EmbeddingFile:
    path: str
    speaker_id: str
    health_status: str
    session: str
    group: str
    vector: torch.Tensor
    sex: str = SEX_M
    age: float = 0.0
    hy: str = "0" # Hoehn & Yahr scale
    dataset_version: str = "v1"

@dataclass
class Centroid:
    type: str  # 'group' or 'speaker'
    speaker_id: str
    group_id: Optional[str]
    vector: torch.Tensor
    sex: str = SEX_M
    age: float = 0.0
    hy: str = "0"
    dataset_version: str = "v1"

def load_metadata(csv_path: str) -> Dict[str, Dict]:
    """
    Loads gender, age and H/Y metadata from PCGITA mapping CSV.
    Returns mapping: SpeakerID -> {'sex': M/F, 'age': float, 'hy': str}
    """
    if not os.path.exists(csv_path):
        return {}
        
    df = pd.read_csv(csv_path, sep=';')
    mapping = {}
    for _, row in df.iterrows():
        sid = row['Code BD-Parkinson']
        mapping[sid] = {
            'sex': row['SEX'],
            'age': float(row['AGE']),
            'hy': str(row['H/Y'])
        }
    return mapping

def parse_filename(filename: str) -> dict:
    name = os.path.splitext(filename)[0]
    parts = name.split('_')
    if len(parts) < 3:
        raise ValueError(f"Filename {filename} does not follow naming convention.")
    
    speaker_id = parts[0]
    health_status = STATUS_PD if STATUS_PD in speaker_id else STATUS_HC
    session = parts[1]
    
    group = 'unknown'
    for g in ALL_GROUPS:
        if g == GROUP_WORDS: continue
        if any(g in p.lower() for p in parts[2:]):
            group = g
            break
            
    if group == 'unknown' and len(parts) >= 6:
        group = GROUP_WORDS
        
    return {
        'speaker_id': speaker_id,
        'health_status': health_status,
        'session': session,
        'group': group
    }

def load_embeddings(directory: str, metadata: Dict[str, Dict] = None, version: str = "v1") -> List[EmbeddingFile]:
    """Loads all .pt files and attaches gender, age and H/Y metadata."""
    files = glob.glob(os.path.join(directory, '*.pt'))
    embeddings = []
    
    for f in files:
        try:
            name = os.path.basename(f)
            md = parse_filename(name)
            vector = torch.load(f, map_location='cpu', weights_only=True)
            
            sex, age, hy = SEX_M, 0.0, "0"
            sid = md['speaker_id']
            if metadata and sid in metadata:
                sex = metadata[sid]['sex']
                age = metadata[sid]['age']
                hy = metadata[sid]['hy']
            
            embeddings.append(EmbeddingFile(
                path=f,
                speaker_id=sid,
                health_status=md['health_status'],
                session=md['session'],
                group=md['group'],
                vector=vector,
                sex=sex,
                age=age,
                hy=hy,
                dataset_version=version
            ))
        except Exception as e:
            print(f"Skipping {f}: {e}")
        
    return embeddings
