import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
from .utils import extract_speaker_id
from .constants import SAMPLING_RATE

class PhonemeComparator:
    def __init__(self):
        self.results = []

    def load_alignment(self, path: Path) -> pd.DataFrame:
        """
        Loads and cleans alignment CSV.
        """
        try:
            df = pd.read_csv(path, sep=';')
            if 'MAU' not in df.columns or 'DURATION' not in df.columns:
                return pd.DataFrame()
            
            # Technical tokens to ignore (standard in this project)
            ignore_tokens = ['<p:>', '<usb>', 'SIL', '']
            df = df[~df['MAU'].isin(ignore_tokens)].copy()
            
            # Convert duration to seconds
            df['duration_sec'] = df['DURATION'] / SAMPLING_RATE
            return df
        except Exception:
            return pd.DataFrame()

    def compare_alignments(self, ref_path: Path, test_path: Path, task: str):
        """
        Compares two phoneme alignment files by sequence.
        """
        ref_df = self.load_alignment(ref_path)
        test_df = self.load_alignment(test_path)

        if ref_df.empty:
            return

        ref_phonemes = ref_df['MAU'].tolist()
        test_phonemes = test_df['MAU'].tolist()
        
        speaker_id = extract_speaker_id(ref_path)
        
        # Simple sequence comparison
        # In a real parallel case, the tokens should match.
        # If lengths differ, we identify missing/extra.
        
        # For simplicity in this P1 task, we compare by index up to min length
        # and report missing tokens if test is shorter.
        
        min_len = min(len(ref_phonemes), len(test_phonemes))
        
        for i in range(min_len):
            ref_p = ref_phonemes[i]
            test_p = test_phonemes[i]
            
            duration_delta = None
            mismatch = ref_p != test_p
            
            if not mismatch:
                duration_delta = abs(ref_df.iloc[i]['duration_sec'] - test_df.iloc[i]['duration_sec'])

            self.results.append({
                "speaker_id": speaker_id,
                "task": task,
                "filename": ref_path.name,
                "index": i,
                "ref_phoneme": ref_p,
                "test_phoneme": test_p,
                "mismatch": mismatch,
                "duration_delta": duration_delta
            })
            
        # Handle missing phonemes in test
        if len(ref_phonemes) > len(test_phonemes):
            for i in range(min_len, len(ref_phonemes)):
                self.results.append({
                    "speaker_id": speaker_id,
                    "task": task,
                    "filename": ref_path.name,
                    "index": i,
                    "ref_phoneme": ref_phonemes[i],
                    "test_phoneme": None,
                    "mismatch": True,
                    "duration_delta": None,
                    "is_missing": True
                })

    def get_report(self) -> pd.DataFrame:
        return pd.DataFrame(self.results)
