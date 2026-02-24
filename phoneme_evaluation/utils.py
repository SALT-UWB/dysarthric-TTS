from pathlib import Path
from typing import List
from .constants import DATA_ROOT, TASKS

def get_alignment_files(task: str) -> List[Path]:
    """Returns a list of all CSV alignment files for a given task."""
    task_dir = DATA_ROOT / task
    if not task_dir.exists():
        return []
    return list(task_dir.glob("*.csv"))

def extract_speaker_id(file_path: Path) -> str:
    """
    Extracts the speaker ID from the filename.
    Typical formats: 001PD_S1_readtext.csv, 041YHC_S1_readtext.csv
    Speaker ID is the prefix before the first underscore or based on naming convention.
    In PC-GITA, usually the first 5-6 characters: 001PD, 041YHC.
    """
    # Simple extraction: split by underscore and take the first part
    return file_path.stem.split('_')[0]

def is_pd(speaker_id: str) -> bool:
    """Quick check for PD based on ID string if applicable (PD in name)."""
    return "PD" in speaker_id.upper()

def is_hc(speaker_id: str) -> bool:
    """Quick check for HC based on ID string if applicable (HC or YHC in name)."""
    return "HC" in speaker_id.upper()
