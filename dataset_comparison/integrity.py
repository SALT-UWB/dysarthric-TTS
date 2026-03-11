import pandas as pd
import logging
from pathlib import Path
from typing import List, Dict, Tuple
from .utils import get_parallel_file, extract_speaker_id
from .constants import TASKS

logger = logging.getLogger(__name__)

class DataIntegrityChecker:
    def __init__(self, ref_root: Path, test_root: Path):
        self.ref_root = ref_root
        self.test_root = test_root
        self.results = []

    def check_parallelism(self):
        """
        Walks through TASKS in ref_root and checks existence in test_root.
        Also triggers transcription comparison.
        """
        for task in TASKS:
            ref_task_dir = self.ref_root / task
            if not ref_task_dir.exists():
                logger.warning(f"Task directory missing in reference: {task}")
                continue

            logger.info(f"Checking parallelism for task: {task}")
            for ref_file in ref_task_dir.glob("*.wav"):
                test_file = get_parallel_file(ref_file, self.test_root)
                
                # Check for parallel CSV
                ref_csv = ref_file.with_suffix(".csv")
                test_csv = get_parallel_file(ref_csv, self.test_root)
                
                # Check for WavLM embeddings
                ref_emb = self.ref_root / "speaker_embeddings" / "wavLM" / (ref_file.stem + ".pt")
                test_emb = self.test_root / "speaker_embeddings" / "wavLM" / (ref_file.stem + ".pt")
                
                if not test_file:
                    logger.warning(f"Missing test audio for: {ref_file.name}")
                if ref_csv.exists() and not test_csv:
                    logger.warning(f"Missing test CSV for: {ref_csv.name}")
                
                txt_match = None
                if test_file:
                    txt_match = self.compare_transcription(ref_file.with_suffix(".txt"), 
                                                         test_file.with_suffix(".txt"))

                self.results.append({
                    "task": task,
                    "speaker_id": extract_speaker_id(ref_file),
                    "filename": ref_file.name,
                    "exists_in_test": test_file is not None,
                    "csv_exists_in_test": test_csv is not None if ref_csv.exists() else None,
                    "emb_exists_in_ref": ref_emb.exists(),
                    "emb_exists_in_test": test_emb.exists(),
                    "transcription_match": txt_match
                })

    def compare_transcription(self, ref_txt: Path, test_txt: Path) -> bool:
        """
        Compares content of two transcription files.
        """
        if not ref_txt.exists():
            logger.debug(f"Reference transcript missing: {ref_txt.name}")
            return False
        if not test_txt.exists():
            logger.warning(f"Test transcript missing: {test_txt.name}")
            return False
        
        try:
            ref_content = ref_txt.read_text(encoding="utf-8").strip()
            test_content = test_txt.read_text(encoding="utf-8").strip()
            
            match = ref_content == test_content
            if not match:
                logger.warning(f"Transcription mismatch in {ref_txt.name}:")
                logger.warning(f"  REF: '{ref_content}'")
                logger.warning(f"  TEST: '{test_content}'")
            return match
        except Exception as e:
            logger.error(f"Error reading transcripts: {e}")
            return False

    def get_report(self) -> pd.DataFrame:
        return pd.DataFrame(self.results)
