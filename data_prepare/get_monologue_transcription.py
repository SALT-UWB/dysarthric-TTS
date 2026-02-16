import os
import re
from pathlib import Path
import pandas as pd

def clean_transcript(text: str) -> str:
    """
    Cleans the transcript according to rules:
    - Lowercase everything.
    - Capitalize the start of every sentence.
    - Remove spaces before punctuation.
    - Add a period at the end if missing.
    """
    if not text:
        return ""
    
    # Lowercase
    text = text.lower().strip()
    
    # Remove spaces before punctuation (., !? : ;)
    # e.g. "word ." -> "word."
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    
    # Ensure it ends with a period if it doesn't end with punctuation
    if text and text[-1] not in '.!?':
        text += '.'
    
    # Sentence capitalization
    # 1. Capitalize first letter of the text
    # 2. Capitalize letters following . ! ? and whitespace
    # Handles Spanish inverted marks (¿, ¡) if present
    def capitalize_match(m):
        # group(1) is the preceding punctuation+space, group(2) is inverted mark, group(3) is the letter
        return m.group(1) + m.group(2) + m.group(3).upper()

    # Regex: (Start of string OR .!? followed by spaces) + (optional ¿¡) + (a letter)
    text = re.sub(r'(^|[.!?]\s+)([¿¡]?)([a-z])', capitalize_match, text)
        
    return text

def main():
    base_path = Path("datalocal/v260210_24kHz")
    monologue_dir = base_path / "monologue"
    metadata_dir = base_path / "_metadata"
    mapping_path = metadata_dir / "PCGITAtoPD_mapping.csv"
    transcripts_path = metadata_dir / "S1_complete_monologue.txt"
    
    if not monologue_dir.exists():
        print(f"Error: Monologue directory not found: {monologue_dir}")
        return

    # Load mapping
    # Header: CODE;CODE4JHU;Code BD-Parkinson;UPDRS;H/Y;SEX;AGE;time after diagnosis
    try:
        mapping_df = pd.read_csv(mapping_path, sep=';')
        # Map 'Code BD-Parkinson' -> 'CODE4JHU'
        id_to_code4jhu = pd.Series(mapping_df.CODE4JHU.values, index=mapping_df['Code BD-Parkinson']).to_dict()
    except Exception as e:
        print(f"Error reading mapping file: {e}")
        return

    # Load transcripts
    # Format: 001_MONOLOGUE_PCGITA TRANSCRIPT...
    transcripts = {}
    try:
        with open(transcripts_path, 'r', encoding='utf-8-sig') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # Split by first space to get the tag and the text
                parts = line.split(' ', 1)
                if len(parts) < 2:
                    continue
                
                tag = parts[0] # e.g. 001_MONOLOGUE_PCGITA
                text = parts[1]
                
                # Extract the numeric part from the tag (e.g. 1 from 001_...)
                match = re.search(r'^(\d+)_', tag)
                if match:
                    code_id = int(match.group(1))
                    transcripts[code_id] = text
                    # if code_id == 1: print(f"DEBUG: Loaded transcript for 1: {text[:50]}...")
    except Exception as e:
        print(f"Error reading transcripts file: {e}")
        return

    # Process audio files
    wav_files = list(monologue_dir.glob("*.wav"))
    print(f"Found {len(wav_files)} WAV files.")
    
    processed_count = 0
    warning_count = 0
    
    for wav_file in wav_files:
        # Example: 001PD_S1_monologue.wav
        # ID is 001PD
        stem = wav_file.stem
        match = re.match(r'^([^_]+)', stem)
        if not match:
            print(f"Warning: Could not extract ID from filename {wav_file.name}")
            warning_count += 1
            continue
            
        recording_id = match.group(1)
        
        if recording_id not in id_to_code4jhu:
            print(f"Warning: No mapping found for ID {recording_id} (file: {wav_file.name})")
            warning_count += 1
            continue
            
        code4jhu = id_to_code4jhu[recording_id]
        
        if code4jhu not in transcripts:
            print(f"Warning: No transcript found for CODE4JHU {code4jhu} (ID: {recording_id}, file: {wav_file.name})")
            warning_count += 1
            continue
            
        # Clean and write transcript
        raw_text = transcripts[code4jhu]
        cleaned_text = clean_transcript(raw_text)
        
        output_path = wav_file.with_suffix('.txt')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
            
        processed_count += 1

    print("\nProcessing complete.")
    print(f"Successfully generated: {processed_count} files.")
    if warning_count > 0:
        print(f"Warnings/Missing: {warning_count} files.")

if __name__ == "__main__":
    main()
