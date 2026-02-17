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
    max_sentence_length: float = 15.0,
    min_duration: float = 2.0,
    min_speech_duration: float = 1.0,
    min_word_count: int = 2,
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

    # 1. Collect potential cut points
    potential_cuts = []
    for i in range(len(df)):
        row = df.iloc[i]
        if row['MAU'] == '<p:>':
            # Sentence Boundary Check
            is_nsb = False
            for j in range(i + 1, len(df)):
                if df.iloc[j]['MAU'] != '<p:>':
                    tid = int(df.iloc[j]['TOKEN'])
                    # Use source_words for capitalization check if possible
                    if 0 <= tid < len(source_words):
                        w = source_words[tid]
                        if w and w[0].isupper():
                            is_nsb = True
                    else:
                        # Fallback to ORT
                        ort = str(df.iloc[j]['ORT'])
                        if ort and ort[0].isupper():
                            is_nsb = True
                    break
            
            # Comma Check (word before this pause)
            is_comma = False
            for j in range(i - 1, -1, -1):
                if df.iloc[j]['MAU'] != '<p:>':
                    tid = int(df.iloc[j]['TOKEN'])
                    if 0 <= tid < len(source_words):
                        if ',' in source_words[tid]:
                            is_comma = True
                    break
            
            pause_dur = samples_to_seconds(int(row['DURATION']), sr)
            mid = calculate_midpoint(int(row['BEGIN']), int(row['DURATION']))
            
            if is_nsb:
                potential_cuts.append({'sample': mid, 'type': 'NSB'})
            elif is_comma:
                potential_cuts.append({'sample': mid, 'type': 'COMMA'})
            elif pause_dur > pause_threshold:
                potential_cuts.append({'sample': mid, 'type': 'PAUSE'})

    # 2. Refine segments (ensure max_len, min_speech, min_words)
    def get_seg_stats(s, e):
        sub = df[(df['BEGIN'] + df['DURATION'] > s) & (df['BEGIN'] < e)]
        words = sub[sub['TOKEN'] >= 0]['TOKEN'].unique()
        speech_samples = 0
        for _, r in sub[sub['MAU'] != '<p:>'].iterrows():
            rs = max(r['BEGIN'], s)
            re = min(r['BEGIN'] + r['DURATION'], e)
            speech_samples += max(0, re - rs)
        return len(words), float(speech_samples) / sr

    # Initial split by NSB
    hard_cuts = [0] + sorted([c['sample'] for c in potential_cuts if c['type'] == 'NSB']) + [total_samples]
    hard_cuts = sorted(list(set(hard_cuts)))
    
    raw_units = []
    for i in range(len(hard_cuts) - 1):
        raw_units.append((hard_cuts[i], hard_cuts[i+1], True)) # (start, end, is_nsb)

    # Sub-split long units
    refined_units = []
    for start, end, is_nsb in raw_units:
        stack = [(start, end, is_nsb)]
        while stack:
            s, e, b = stack.pop()
            dur = samples_to_seconds(e - s, sr)
            
            if dur <= max_sentence_length:
                refined_units.append((s, e, b))
                continue
                
            # Try splitting
            inner = [c for c in potential_cuts if s < c['sample'] < e and c['type'] != 'NSB']
            split_found = False
            for ptype in ['COMMA', 'PAUSE']:
                candidates = [c for c in inner if c['type'] == ptype]
                if not candidates: continue
                
                mid_s = s + (e - s) // 2
                candidates.sort(key=lambda x: abs(x['sample'] - mid_s))
                
                for c in candidates:
                    w1, sp1 = get_seg_stats(s, c['sample'])
                    w2, sp2 = get_seg_stats(c['sample'], e)
                    if w1 >= min_word_count and sp1 >= min_speech_duration and \
                       w2 >= min_word_count and sp2 >= min_speech_duration:
                        stack.append((c['sample'], e, b))
                        stack.append((s, c['sample'], False))
                        split_found = True
                        break
                if split_found: break
            
            if not split_found:
                # If still too long, split at the largest available pause in the middle area
                pauses = df[(df['MAU'] == '<p:>') & (df['BEGIN'] > s) & (df['BEGIN'] + df['DURATION'] < e)]
                if not pauses.empty:
                    # Sort by duration descending
                    pauses = pauses.sort_values('DURATION', ascending=False)
                    best_pause = pauses.iloc[0]
                    mid_p = calculate_midpoint(int(best_pause['BEGIN']), int(best_pause['DURATION']))
                    
                    stack.append((mid_p, e, b))
                    stack.append((s, mid_p, False))
                else:
                    # Absolute fallback: force split in the middle
                    mid_abs = s + (e - s) // 2
                    stack.append((mid_abs, e, b))
                    stack.append((s, mid_abs, False))

    # Final Merge Pass for invalid segments
    refined_units.sort(key=lambda x: x[0])
    segments: list[tuple[int, int, bool]] = []
    
    for s, e, b in refined_units:
        w, sp = get_seg_stats(s, e)
        # Check if merging with previous would violate max_sentence_length
        if w >= min_word_count and sp >= min_speech_duration:
            segments.append((s, e, b))
        else:
            if segments:
                ls, le, lb = segments[-1]
                merged_dur = samples_to_seconds(e - ls, sr)
                if merged_dur <= max_sentence_length:
                    segments.pop()
                    segments.append((ls, e, b))
                else:
                    # Cannot merge without violating length, keep as is
                    segments.append((s, e, b))
            else:
                segments.append((s, e, b))

    # Clean up any remaining invalid at the start by merging with next
    if len(segments) > 1:
        s, e, b = segments[0]
        w, sp = get_seg_stats(s, e)
        if w < min_word_count or sp < min_speech_duration:
            ns, ne, nb = segments.pop(1)
            segments[0] = (s, ne, nb)

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
            leading_excess = max(0, leading_sil_samples - max_silence_samples)
            trailing_excess = max(0, trailing_sil_samples - max_silence_samples)
            total_excess = leading_excess + trailing_excess
            
            current_samples = end - start
            min_samples = int(min_duration * sr)
            max_to_remove = max(0, current_samples - min_samples)
            
            if total_excess > max_to_remove:
                # We can't remove all excess silence. Remove as much as allowed.
                if total_excess > 0:
                    scale = max_to_remove / total_excess
                    leading_to_remove = int(leading_excess * scale)
                    trailing_to_remove = int(max_to_remove - leading_to_remove)
                else:
                    leading_to_remove = 0
                    trailing_to_remove = 0
                logger.warning(f"  Segment {idx:03d}: partial cropping to maintain {min_duration}s")
            else:
                leading_to_remove = leading_excess
                trailing_to_remove = trailing_excess

            actual_start = start + leading_to_remove
            actual_end = end - trailing_to_remove
            
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
        # Identify word blocks (contiguous TOKEN >= 0) to check for gaps
        word_blocks = seg_df[seg_df['TOKEN'] >= 0].groupby('TOKEN', sort=False).agg({
            'BEGIN': 'min',
            'DURATION': 'sum'
        }).reset_index()
        
        words_with_commas = []
        for i in range(len(word_blocks)):
            tid = int(word_blocks.iloc[i]['TOKEN'])
            if 0 <= tid < len(source_words):
                word_text = source_words[tid]
            else:
                # Fallback to ORT if token is out of bounds
                fallback_ort = seg_df[seg_df['TOKEN'] == tid]['ORT'].iloc[0]
                word_text = str(fallback_ort)
            
            words_with_commas.append(word_text)
            
            # Check for gap to next word (> 250ms)
            if i < len(word_blocks) - 1:
                curr_end = word_blocks.iloc[i]['BEGIN'] + word_blocks.iloc[i]['DURATION']
                next_start = word_blocks.iloc[i+1]['BEGIN']
                gap_sec = samples_to_seconds(next_start - curr_end, sr)
                if gap_sec >= 0.250:
                    # Add comma if word doesn't already have punctuation
                    if words_with_commas[-1] and words_with_commas[-1][-1] not in ".,!?;:":
                        words_with_commas[-1] += ","
            
        seg_text = " ".join(words_with_commas)
        
        # Add comma if split in middle of sentence
        if not is_boundary and seg_text and seg_text[-1] not in ".,!?;:":
            seg_text += ","
            
        # Add dot at the end if no punctuation present
        if seg_text and seg_text[-1] not in ".,!?;:":
            seg_text += "."
            
        with open(output_dir / f"{seg_stem}.txt", 'w', encoding='utf-8') as f:
            f.write(seg_text)
            
        processed_segments.append({
            'id': seg_stem,
            'duration_sec': samples_to_seconds(actual_end - actual_start, sr),
            'word_count': len(words_with_commas)
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
    parser.add_argument("--max_sentence_length", type=float, default=15.0, 
                        help="Maximum segment duration in seconds")
    parser.add_argument("--min_duration", type=float, default=2.0, 
                        help="Minimum total segment duration in seconds (used for cropping safety)")
    parser.add_argument("--min_speech_duration", type=float, default=1.0, 
                        help="Minimum speech duration (excluding pauses) in seconds")
    parser.add_argument("--min_word_count", type=int, default=2, 
                        help="Minimum number of words per segment")
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
            max_sentence_length=args.max_sentence_length,
            min_duration=args.min_duration,
            min_speech_duration=args.min_speech_duration,
            min_word_count=args.min_word_count,
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
