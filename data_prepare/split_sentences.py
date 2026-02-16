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
    max_silence_ms: float = -1.0,
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

    # Read source text for reference (to preserve punctuation)
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            source_words = f.read().split()
    except Exception as e:
        logger.error(f"Error reading {txt_path}: {e}")
        return 0, []

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

    # 1. Collect potential cut points (sample, is_sentence_boundary)
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
                candidate_cuts.append((calculate_midpoint(int(row['BEGIN']), int(row['DURATION'])), is_sentence_boundary))

    # 2. Refine segments (ensure min_duration and presence of speech)
    # Each entry: (start, end, ends_at_sentence_boundary)
    segments: list[tuple[int, int, bool]] = []
    current_start = 0
    
    for cut, is_boundary in candidate_cuts:
        if cut <= current_start:
            continue
            
        # Check current candidate segment
        seg_dur = samples_to_seconds(cut - current_start, sr)
        seg_df_initial = df[(df['BEGIN'] + df['DURATION'] > current_start) & (df['BEGIN'] < cut)]
        has_speech = not seg_df_initial[seg_df_initial['ORT'].str.strip() != '<p:>'].empty if 'ORT' in df.columns else False
        
        # Only commit cut if segment is valid OR if it's the very last part (handled after loop)
        if seg_dur >= min_duration and has_speech:
            segments.append((current_start, cut, is_boundary))
            current_start = cut
            
    # Add the remaining tail to the last segment or create new if valid
    if current_start < total_samples:
        final_dur = samples_to_seconds(total_samples - current_start, sr)
        final_df = df[(df['BEGIN'] + df['DURATION'] > current_start)]
        final_has_speech = not final_df[final_df['ORT'].str.strip() != '<p:>'].empty
        
        if segments and (final_dur < min_duration or not final_has_speech):
            # Merge with previous; the boundary status of the merged segment is True (end of file)
            prev_start, _, _ = segments.pop()
            segments.append((prev_start, total_samples, True))
        else:
            segments.append((current_start, total_samples, True))

    # 3. Write segments
    audio, _ = sf.read(str(wav_path))
    processed_segments = []
    
    max_silence_samples = int((max_silence_ms * sr) / 1000) if max_silence_ms > 0 else -1

    logger.info(f"Processing {stem}: {samples_to_seconds(total_samples, sr):.2f}s, {len(segments)} segments")

    for idx, (start, end, is_boundary) in enumerate(segments, 1):
        actual_start, actual_end = start, end
        
        # Calculate original leading silence for this segment (for logging)
        leading_sil_samples = 0
        r0_mask = (df['BEGIN'] <= start) & (df['BEGIN'] + df['DURATION'] > start)
        if not df[r0_mask].empty:
            r0 = df[r0_mask].iloc[0]
            if r0['MAU'] == '<p:>':
                leading_sil_samples = (r0['BEGIN'] + r0['DURATION']) - start

        # Calculate original trailing silence for this segment (for logging)
        trailing_sil_samples = 0
        rn_mask = (df['BEGIN'] < end) & (df['BEGIN'] + df['DURATION'] >= end)
        if not df[rn_mask].empty:
            rn = df[rn_mask].iloc[-1]
            if rn['MAU'] == '<p:>':
                trailing_sil_samples = end - rn['BEGIN']

        # 3a. Crop leading/trailing silence if requested
        if max_silence_samples >= 0:
            proposed_start = actual_start
            proposed_end = actual_end
            
            if leading_sil_samples > max_silence_samples:
                proposed_start = (start + leading_sil_samples) - max_silence_samples
            if trailing_sil_samples > max_silence_samples:
                proposed_end = (end - trailing_sil_samples) + max_silence_samples
            
            # Check if the cropped segment still meets min_duration
            if samples_to_seconds(proposed_end - proposed_start, sr) >= min_duration:
                actual_start = proposed_start
                actual_end = proposed_end
            else:
                logger.warning(f"  Segment {idx:03d}: skipped cropping (would be shorter than {min_duration}s)")
            
            if actual_start >= actual_end:
                logger.warning(f"  Segment {idx:03d}: skipped (cropped to zero length)")
                continue

        seg_suffix = f"{idx:03d}"
        seg_stem = f"{stem}_{seg_suffix}"
        
        # WAV
        seg_audio = audio[actual_start:actual_end]
        sf.write(str(output_dir / f"{seg_stem}.wav"), seg_audio, sr)
        
        # CSV (Filtered and Shifted)
        seg_df = df[(df['BEGIN'] + df['DURATION'] > actual_start) & (df['BEGIN'] < actual_end)].copy()
        
        # Clip rows at boundaries and shift
        def clip_and_shift(row: pd.Series) -> pd.Series:
            old_begin = int(row['BEGIN'])
            old_dur = int(row['DURATION'])
            
            # Clip start
            new_begin_abs = max(old_begin, actual_start)
            # Clip end
            new_end_abs = min(old_begin + old_dur, actual_end)
            
            row['BEGIN'] = new_begin_abs - actual_start
            row['DURATION'] = max(0, new_end_abs - new_begin_abs)
            return row

        seg_df = seg_df.apply(clip_and_shift, axis=1)
        seg_df = seg_df[seg_df['DURATION'] > 0]
        seg_df.to_csv(output_dir / f"{seg_stem}.csv", sep=csv_delimiter, index=False)
        
        # TXT
        # Get unique TOKEN IDs in this segment (ignoring -1)
        seg_token_ids = sorted(seg_df[seg_df['TOKEN'] >= 0]['TOKEN'].unique().tolist())
        
        # Map tokens to words from the original source text
        words = []
        for tid in seg_token_ids:
            if 0 <= tid < len(source_words):
                words.append(source_words[tid])
            else:
                # Fallback to ORT if token is out of bounds
                fallback_ort = seg_df[seg_df['TOKEN'] == tid]['ORT'].iloc[0]
                words.append(str(fallback_ort))
            
        seg_text = " ".join(words)
        
        # Add comma if split in middle of sentence
        if not is_boundary and seg_text and seg_text[-1] not in ".,!?;:":
            seg_text += ","
            
        with open(output_dir / f"{seg_stem}.txt", 'w', encoding='utf-8') as f:
            f.write(seg_text)
            
        processed_segments.append({
            'id': seg_stem,
            'duration_sec': samples_to_seconds(actual_end - actual_start, sr),
            'word_count': len(words)
        })

        # Log segment details
        l_ms = (leading_sil_samples / sr) * 1000
        t_ms = (trailing_sil_samples / sr) * 1000
        logger.info(f"  Segment {idx:03d}: {samples_to_seconds(actual_end - actual_start, sr):.2f}s (leading sil: {l_ms:.0f}ms, trailing sil: {t_ms:.0f}ms) - \"{seg_text}\"")
        
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
    parser.add_argument("--max_silence_ms", type=float, default=-1.0, 
                        help="Maximum leading/trailing silence in milliseconds. Default -1 (keep all).")
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
            max_silence_ms=args.max_silence_ms,
            csv_delimiter=args.csv_delimiter,
            expected_sr=args.expected_sr
        )
        
        if count > 0:
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
