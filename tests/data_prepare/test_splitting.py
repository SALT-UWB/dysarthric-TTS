import pytest
from pathlib import Path
import pandas as pd
import numpy as np
import soundfile as sf
import sys
import os

# Add root to sys.path to import data_prepare
sys.path.append(str(Path(__file__).parent.parent.parent))

# We'll import these once implemented, for now we might need to mock or define expected behavior
# from data_prepare.split_sentences import calculate_midpoint, samples_to_seconds

def test_samples_to_seconds():
    # Placeholder for actual implementation import
    from data_prepare.split_sentences import samples_to_seconds
    assert samples_to_seconds(24000, 24000) == 1.0
    assert samples_to_seconds(12000, 24000) == 0.5

def test_calculate_midpoint():
    from data_prepare.split_sentences import calculate_midpoint
    # BEGIN=100, DURATION=50 -> Midpoint = 100 + 25 = 125
    assert calculate_midpoint(100, 50) == 125

def test_cli_splitting(tmp_path):
    # Integration test using dummy data
    from data_prepare.split_sentences import main
    
    dummy_dir = Path(__file__).parent / "dummy_data"
    output_dir = tmp_path / "output"
    
    # Run main logic
    # Mocking sys.argv or calling main with args
    args = [
        "--input_dir", str(dummy_dir),
        "--output_dir", str(output_dir),
        "--expected_sr", "24000"
    ]
    
    # Since we haven't implemented main yet, this will fail.
    # We will use a wrapper or just call the function.
    import argparse
    from unittest.mock import patch
    
    with patch('sys.argv', ['split_sentences.py'] + args):
        main()
    
    # Verify outputs for 001PD_S1_readtext
    # Expected segments: 
    # 1: 0 to midpoint of second pause (48000 + 24000/2 = 60000)
    # 2: 60000 to end
    
    stem = "001PD_S1_readtext"
    assert (output_dir / f"{stem}_001.wav").exists()
    assert (output_dir / f"{stem}_001.txt").exists()
    assert (output_dir / f"{stem}_001.csv").exists()
    assert (output_dir / f"{stem}_002.wav").exists()
    
    # Verify 041YHC_S1_readtext (should split on > 1s pause at midpoint of 36000-72000)
    stem_hc = "041YHC_S1_readtext"
    assert (output_dir / f"{stem_hc}_001.wav").exists()
    assert (output_dir / f"{stem_hc}_002.wav").exists()
