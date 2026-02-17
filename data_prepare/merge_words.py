import argparse
import sys
from pathlib import Path
from typing import Any
import pandas as pd
import numpy as np
import soundfile as sf
import re

# Add root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from data_prepare.audio_utils import get_sampling_rate
from data_prepare.utils import ensure_dir, setup_logging

logger = setup_logging(__name__)

def get_word_list(txt_path: Path) -> list[str]:
    """Reads words from a text file, stripping trailing punctuation for naming."""
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()
            # Split by whitespace, then clean each word for filename use
            words = text.split()
            # Remove characters not allowed in filenames or that are just punctuation
            clean_words = [re.sub(r'[^a-zA-Z0-9]', '', w) for w in words]
            return [w for w in clean_words if w]
    except Exception as e:
        logger.error(f"Error reading {txt_path}: {e}")
        return []

def merge_segments(
    prefix: str,
    segments: list[dict[str, Any]],
    output_dir: Path,
    csv_delimiter: str = ';'
) -> None:
    """Concatenates multiple segments into one triple (WAV, TXT, CSV)."""
    if not segments:
        return

    all_audio = []
    all_txt = []
    all_csv = []
    all_words_for_name = []
    
    current_offset_samples = 0
    sr = segments[0]['sr']

    for seg in segments:
        # Audio
        audio, _ = sf.read(str(seg['wav_path']))
        all_audio.append(audio)
        
        # Text
        with open(seg['txt_path'], 'r', encoding='utf-8') as f:
            all_txt.append(f.read().strip())
        
        # Word list for name
        all_words_for_name.extend(seg['clean_words'])
        
        # CSV (Alignment)
        df = pd.read_csv(seg['csv_path'], sep=csv_delimiter)
        df['BEGIN'] = df['BEGIN'] + current_offset_samples
        all_csv.append(df)
        
        current_offset_samples += len(audio)

    # 1. Join Audio
    merged_audio = np.concatenate(all_audio)
    
    # 2. Join Text
    merged_txt = " ".join(all_txt)
    
    # 3. Join CSV
    merged_csv = pd.concat(all_csv, ignore_index=True)
    
    # 4. Generate Name
    # Prefix + underscore joined words
    words_part = "_".join(all_words_for_name)
    merged_stem = f"{prefix}_{words_part}"
    
    # Write files
    sf.write(str(output_dir / f"{merged_stem}.wav"), merged_audio, sr)
    
    with open(output_dir / f"{merged_stem}.txt", 'w', encoding='utf-8') as f:
        f.write(merged_txt)
        
    merged_csv.to_csv(output_dir / f"{merged_stem}.csv", sep=csv_delimiter, index=False)
    
    logger.info(f"Generated merged segment: {merged_stem} ({len(all_words_for_name)} words)")

def main() -> None:
    parser = argparse.ArgumentParser(description="Merge short segments into ~5 word units.")
    parser.add_argument("--input_dir", required=True, type=str, 
                        help="Directory containing segmented *.wav, *.txt, *.csv")
    parser.add_argument("--output_dir", required=True, type=str, 
                        help="Where to write merged artifacts")
    parser.add_argument("--csv_delimiter", type=str, default=";", 
                        help="CSV delimiter")
    
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    output_dir = ensure_dir(args.output_dir)
    
    wav_files = sorted(list(input_dir.glob("*.wav")))
    
    # Group by speaker/session prefix (e.g. 001PD_S1)
    # Filename format expected: {prefix}_{index}.wav
    groups = {}
    for wav_path in wav_files:
        stem = wav_path.stem
        # Split from right once to separate the index/suffix added by split_sentences
        parts = stem.rsplit('_', 1)
        if len(parts) < 2:
            logger.warning(f"File {wav_path.name} does not follow expected naming convention. Skipping.")
            continue
            
        prefix = parts[0]
        if prefix not in groups:
            groups[prefix] = []
            
        txt_path = wav_path.with_suffix('.txt')
        csv_path = wav_path.with_suffix('.csv')
        
        if not (txt_path.exists() and csv_path.exists()):
            continue
            
        clean_words = get_word_list(txt_path)
        if not clean_words:
            continue
            
        groups[prefix].append({
            'wav_path': wav_path,
            'txt_path': txt_path,
            'csv_path': csv_path,
            'clean_words': clean_words,
            'word_count': len(clean_words),
            'sr': get_sampling_rate(wav_path)
        })

    for prefix, segments in groups.items():
        logger.info(f"Processing prefix {prefix}: {len(segments)} source segments")
        
        i = 0
        while i < len(segments):
            current_batch = []
            batch_word_count = 0
            
            # Goal: target 5 words
            while i < len(segments):
                seg = segments[i]
                current_batch.append(seg)
                batch_word_count += seg['word_count']
                i += 1
                
                if batch_word_count >= 5:
                    # Check remainder for this prefix
                    remaining_words = sum(s['word_count'] for s in segments[i:])
                    # If remaining < 4, we must keep going and include them in this batch
                    if remaining_words > 0 and remaining_words < 4:
                        continue
                    else:
                        break
            
            # Final check: if we finished but this batch has < 4 words (and isn't the only batch)
            # This logic is mostly covered by the look-ahead above, 
            # but handles the very last leftovers if they are extremely short.
            # In practice, if total words for a prefix < 4, we just output it as is.
            
            merge_segments(prefix, current_batch, output_dir, args.csv_delimiter)

if __name__ == "__main__":
    main()
