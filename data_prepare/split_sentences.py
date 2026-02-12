import argparse
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import soundfile as sf

# Add root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from data_prepare.audio_utils import get_duration_samples, get_sampling_rate
from data_prepare.utils import ensure_dir, setup_logging

logger = setup_logging(__name__)

def samples_to_seconds(samples: int, sr: int) -> float:
    """Converts samples to seconds."""
    return float(samples) / sr

def calculate_midpoint(begin: int, duration: int) -> int:
    """Calculates the midpoint of an interval in samples."""
    return int(begin + (duration / 2))

def split_recording(
    stem: str, 
    input_dir: Path, 
    alignment_dir: Path, 
    output_dir: Path, 
    pause_threshold: float = 1.0, 
    min_duration: float = 2.0,
    csv_delimiter: str = ';', 
    expected_sr: int = 24000
) -> tuple[int, list[dict[str, Any]]]:
    """Processes a single recording and splits it into segments."""
    wav_path = input_dir / f"{stem}.wav"
    txt_path = input_dir / f"{stem}.txt"
    csv_path = alignment_dir / f"{stem}.csv"
    
    if not (wav_path.exists() and txt_path.exists() and csv_path.exists()):
        logger.warning(f"Skipping {stem}: Missing one or more files (wav, txt, csv)")
        return 0, []

    # Read audio metadata
    sr = get_sampling_rate(wav_path)
    total_samples = get_duration_samples(wav_path)
    
    if sr != expected_sr:
        logger.error(f"FAIL LOUDLY: {stem}.wav sampling rate is {sr}, expected {expected_sr}")
        sys.exit(1)

    # Read alignment CSV
    try:
        df = pd.read_csv(csv_path, sep=csv_delimiter)
        # Ensure ORT column exists and handle NaNs (empty cells)
        if 'ORT' in df.columns:
            df['ORT'] = df['ORT'].fillna('').astype(str)
    except Exception as e:
        logger.error(f"Error reading {csv_path}: {e}")
        return 0, []

    # Validate alignment timeline
    max_sample = (df['BEGIN'] + df['DURATION']).max()
    if max_sample > total_samples:
        err_msg = (
            f"FAIL LOUDLY: {stem} alignment exceeds audio duration "
            f"({max_sample} > {total_samples})"
        )
        logger.error(err_msg)
        sys.exit(1)

    # 1. Collect potential cut points
    candidate_cuts = []
    for i in range(len(df)):
        row = df.iloc[i]
        if row['MAU'] == '<p:>':
            # Sentence Boundary Check
            is_sentence_boundary = False
            for j in range(i + 1, len(df)):
                if df.iloc[j]['MAU'] != '<p:>':
                    ort = str(df.iloc[j]['ORT'])
                    if ort and ort[0].isupper():
                        is_sentence_boundary = True
                    break
            
            pause_dur = samples_to_seconds(int(row['DURATION']), sr)
            if is_sentence_boundary or pause_dur > pause_threshold:
                candidate_cuts.append(calculate_midpoint(int(row['BEGIN']), int(row['DURATION'])))

    # 2. Refine segments (ensure min_duration and presence of speech)
    segments: list[tuple[int, int]] = []
    current_start = 0
    
    for cut in candidate_cuts:
        if cut <= current_start:
            continue
            
        # Check current candidate segment
        seg_dur = samples_to_seconds(cut - current_start, sr)
        seg_df = df[(df['BEGIN'] + df['DURATION'] > current_start) & (df['BEGIN'] < cut)]
        has_speech = not seg_df[seg_df['ORT'].str.strip() != '<p:>'].empty if 'ORT' in df.columns else False
        
        # Only commit cut if segment is valid OR if it's the very last part (handled after loop)
        if seg_dur >= min_duration and has_speech:
            segments.append((current_start, cut))
            current_start = cut
            
    # Add the remaining tail to the last segment or create new if valid
    if current_start < total_samples:
        final_dur = samples_to_seconds(total_samples - current_start, sr)
        final_df = df[(df['BEGIN'] + df['DURATION'] > current_start)]
        final_has_speech = not final_df[final_df['ORT'].str.strip() != '<p:>'].empty
        
        if segments and (final_dur < min_duration or not final_has_speech):
            # Merge with previous
            prev_start, _ = segments.pop()
            segments.append((prev_start, total_samples))
        else:
            segments.append((current_start, total_samples))

    # 3. Write segments
    audio, _ = sf.read(str(wav_path))
    processed_segments = []
    
    for idx, (start, end) in enumerate(segments, 1):
        seg_suffix = f"{idx:03d}"
        seg_stem = f"{stem}_{seg_suffix}"
        
        # WAV
        seg_audio = audio[start:end]
        sf.write(str(output_dir / f"{seg_stem}.wav"), seg_audio, sr)
        
        # CSV (Filtered and Shifted)
        seg_df = df[(df['BEGIN'] + df['DURATION'] > start) & (df['BEGIN'] < end)].copy()
        
        # Clip rows at boundaries and shift
        def clip_and_shift(row: pd.Series) -> pd.Series:
            old_begin = int(row['BEGIN'])
            old_dur = int(row['DURATION'])
            old_end = old_begin + old_dur
            
            # Clip start
            new_begin_abs = max(old_begin, start)
            # Clip end
            new_end_abs = min(old_end, end)
            
            row['BEGIN'] = new_begin_abs - start
            row['DURATION'] = max(0, new_end_abs - new_begin_abs)
            return row

        seg_df = seg_df.apply(clip_and_shift, axis=1)
        # Remove rows that became 0 duration due to clipping
        seg_df = seg_df[seg_df['DURATION'] > 0]
        
        seg_df.to_csv(output_dir / f"{seg_stem}.csv", sep=csv_delimiter, index=False)
        
        # TXT
        # Deduplicate words using the TOKEN column
        # Each unique non-negative TOKEN corresponds to one word
        speech_df = seg_df[(seg_df['TOKEN'] >= 0) & (seg_df['ORT'].str.strip() != '<p:>')]
        
        # Group by TOKEN and take the first ORT for each
        if not speech_df.empty:
            words = speech_df.groupby('TOKEN', sort=True)['ORT'].first().astype(str).tolist()
        else:
            words = []
            
        seg_text = " ".join(words)
        with open(output_dir / f"{seg_stem}.txt", 'w', encoding='utf-8') as f:
            f.write(seg_text)
            
        processed_segments.append({
            'id': seg_stem,
            'duration_sec': samples_to_seconds(end - start, sr),
            'word_count': len(words)
        })
        
    return len(segments), processed_segments

def main() -> None:
    parser = argparse.ArgumentParser(description="Split PC-GITA recordings into sentences.")
    parser.add_argument("--input_dir", required=True, type=str, 
                        help="Directory containing *.wav and *.txt")
    parser.add_argument("--alignment_dir", type=str, 
                        help="Directory containing *.csv")
    parser.add_argument("--output_dir", required=True, type=str, 
                        help="Where to write segmented artifacts")
    parser.add_argument("--pause_threshold", type=float, default=1.0, 
                        help="Pause threshold in seconds")
    parser.add_argument("--min_duration", type=float, default=2.0, 
                        help="Minimum segment duration in seconds")
    parser.add_argument("--csv_delimiter", type=str, default=";", 
                        help="CSV delimiter")
    parser.add_argument("--expected_sr", type=int, default=24000, 
                        help="Expected sampling rate")
    
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    alignment_dir = Path(args.alignment_dir) if args.alignment_dir else input_dir / "ali_phoneme"
    output_dir = ensure_dir(args.output_dir)
    
    wav_files = list(input_dir.glob("*.wav"))
    logger.info(f"Found {len(wav_files)} WAV files in {input_dir}")
    
    summary = []
    failed = []
    
    for wav_file in wav_files:
        stem = wav_file.stem
        count, segments = split_recording(
            stem, input_dir, alignment_dir, output_dir,
            pause_threshold=args.pause_threshold,
            min_duration=args.min_duration,
            csv_delimiter=args.csv_delimiter,
            expected_sr=args.expected_sr
        )
        
        if count > 0:
            logger.info(f"Processed {stem}: generated {count} segments")
            summary.extend(segments)
        else:
            failed.append(stem)
            
    # Summary report
    logger.info("\n--- Run Summary ---")
    logger.info(f"Total source files processed: {len(wav_files) - len(failed)}")
    logger.info(f"Total segments generated: {len(summary)}")
    if failed:
        logger.info(f"Skipped/Failed files: {', '.join(failed)}")

if __name__ == "__main__":
    main()
