import re
from pathlib import Path
from typing import Optional

def extract_speaker_id(path: Path) -> str:
    """
    Extracts the speaker ID (e.g., 001PD) from a filename.
    Expected format: [ID][STATUS]_...
    """
    filename = path.name
    match = re.match(r"(\d{3}[A-Z]+)", filename)
    if match:
        return match.group(1)
    return "unknown"

def identify_task(filename: str) -> str:
    """
    Identifies the task based on filename patterns.
    - Contains 'ddk': ddk
    - Contains 'monologue': monologue_split
    - Contains 'readtext': readtext_split
    - Contains 'sentence': sentences_cleaned
    - Contains 4+ words (3+ underscores after ID): words_merged
    """
    fn = filename.lower()
    if "ddk" in fn:
        return "ddk"
    if "monologue" in fn:
        return "monologue_split"
    if "readtext" in fn:
        return "readtext_split"
    if "sentence" in fn:
        return "sentences_cleaned"
    
    # Check for words_merged pattern: ID_S1_word1_word2_word3_word4_word5
    # Counting underscores: speakerID(0) _ session(1) _ word1(2) _ word2(3) _ word3(4) _ ...
    if fn.count("_") >= 4:
        return "words_merged"
        
    return "unknown"

def get_parallel_file(file_path: Path, target_dir: Path) -> Optional[Path]:
    """
    Finds the corresponding file in a different directory tree.
    """
    task = identify_task(file_path.name)
    if task == "unknown":
        return None
        
    # Find files recursively in the target task directory to be safe
    task_dir = target_dir / task
    if not task_dir.exists():
        return None
        
    target_file = task_dir / file_path.name
    return target_file if target_file.exists() else None
