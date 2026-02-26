import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd
import soundfile as sf

# Add root to sys.path to import local modules
sys.path.append(str(Path(__file__).parent.parent))

from data_prepare.audio_utils import get_sampling_rate
from data_prepare.utils import ensure_dir, setup_logging

logger = setup_logging(__name__)

def get_duration_sec(wav_path: Path) -> float:
    """Returns duration of a WAV file in seconds."""
    try:
        info = sf.info(str(wav_path))
        return info.frames / info.samplerate
    except Exception:
        return 0.0

def merge_segments(
    speaker_id: str,
    segments: list[dict[str, Any]],
    output_dir: Path,
    source_name: str,
    csv_delimiter: str = ';'
) -> None:
    """Concatenates multiple segments into one triple (WAV, TXT, CSV)."""
    if not segments:
        return

    all_audio = []
    all_txt_segments = []
    all_csv = []
    
    current_offset_samples = 0
    current_token_offset = 0
    sr = segments[0]['sr']

    for seg in segments:
        audio, _ = sf.read(str(seg['wav_path']))
        all_audio.append(audio)
        
        with open(seg['txt_path'], 'r', encoding='utf-8') as f:
            txt = f.read().strip()
            all_txt_segments.append(txt)
        
        df = pd.read_csv(seg['csv_path'], sep=csv_delimiter)
        df['BEGIN'] = df['BEGIN'] + current_offset_samples
        
        if 'TOKEN' in df.columns:
            max_token_in_seg = df['TOKEN'].max()
            df.loc[df['TOKEN'] >= 0, 'TOKEN'] = df.loc[df['TOKEN'] >= 0, 'TOKEN'] + current_token_offset
            if max_token_in_seg >= 0:
                current_token_offset += (int(max_token_in_seg) + 1)
        
        all_csv.append(df)
        current_offset_samples += len(audio)

    merged_audio = np.concatenate(all_audio)
    merged_txt = " ".join(all_txt_segments)
    merged_csv = pd.concat(all_csv, ignore_index=True)
    
    if source_name == "sentence6":
        merged_stem = f"{speaker_id}_sentence6"
    else:
        # Extract segment IDs
        segment_ids = "_".join([seg['wav_path'].stem.split('_')[-1] for seg in segments])
        merged_stem = f"{speaker_id}_{segment_ids}"
    
    sf.write(str(output_dir / f"{merged_stem}.wav"), merged_audio, sr)
    with open(output_dir / f"{merged_stem}.txt", 'w', encoding='utf-8') as f:
        f.write(merged_txt)
    merged_csv.to_csv(output_dir / f"{merged_stem}.csv", sep=csv_delimiter, index=False)
    
    logger.info(f"Generated speaker reference for {speaker_id} from {source_name} ({len(segments)} segments)")

def find_suitable_sentence(
    input_dir: Path, 
    speaker_id: str, 
    pattern: str, 
    min_dur: float = 3.0, 
    max_dur: float = 4.0,
    must_end_with_dot: bool = True
) -> list[dict[str, Any]]:
    """Finds the first segment that fits duration and optional dot criteria."""
    wavs = sorted(list(input_dir.glob(f"{speaker_id}_*_{pattern}_*.wav")))
    
    for wav_path in wavs:
        dur = get_duration_sec(wav_path)
        if not (min_dur <= dur <= max_dur):
            continue
            
        txt_path = wav_path.with_suffix('.txt')
        csv_path = wav_path.with_suffix('.csv')
        
        if not (txt_path.exists() and csv_path.exists()):
            continue
            
        if must_end_with_dot:
            text = txt_path.read_text(encoding='utf-8').strip()
            if not text.endswith('.'):
                continue
            
        return [{
            'wav_path': wav_path,
            'txt_path': txt_path,
            'csv_path': csv_path,
            'sr': get_sampling_rate(wav_path)
        }]
            
    return []

def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare speaker reference audio (Enhanced Sentence 6 variant).")
    parser.add_argument("--base_dir", type=str, default="datalocal/PC-GITA_v260210_24kHz")
    parser.add_argument("--output_dir", type=str, default="datalocal/PC-GITA_v260210_24kHz/speakers_ref_sentence6")
    args = parser.parse_args()
    
    base_dir = Path(args.base_dir)
    sent_dir = base_dir / "sentences_cleaned"
    read_dir = base_dir / "readtext_split"
    mono_dir = base_dir / "monologue_split"
    output_dir = ensure_dir(args.output_dir)
    
    # 1. Identify all speakers from all sources
    all_dirs = [sent_dir, read_dir, mono_dir]
    all_wavs = []
    for d in all_dirs:
        if d.exists():
            all_wavs.extend(list(d.glob("*.wav")))
            
    all_speakers = sorted(list(set(w.name.split('_')[0] for w in all_wavs)))
    logger.info(f"Found {len(all_speakers)} total speakers across all sources.")
    
    stats = {"sentence6": 0, "readtext_perfect": 0, "monologue_perfect": 0, "flexible": 0, "failed": 0}
    
    for spk in all_speakers:
        # Tier 1: Primary - Sentence 6
        s6_wavs = sorted(list(sent_dir.glob(f"{spk}_*_sentence6_*.wav"))) if sent_dir.exists() else []
        if s6_wavs:
            segments = []
            for wav_path in s6_wavs:
                txt_path = wav_path.with_suffix('.txt')
                csv_path = wav_path.with_suffix('.csv')
                if txt_path.exists() and csv_path.exists():
                    segments.append({'wav_path': wav_path, 'txt_path': txt_path, 'csv_path': csv_path, 'sr': get_sampling_rate(wav_path)})
            if segments:
                prefix = segments[0]['wav_path'].stem.rsplit('_', 2)[0]
                merge_segments(prefix, segments, output_dir, "sentence6")
                stats["sentence6"] += 1
                continue

        # Tier 2: Perfect Readtext (3-4s + dot)
        segments = find_suitable_sentence(read_dir, spk, "readtext", 3.0, 4.0, True) if read_dir.exists() else []
        if segments:
            prefix = segments[0]['wav_path'].stem.rsplit('_', 1)[0]
            merge_segments(prefix, segments, output_dir, "readtext_perfect")
            stats["readtext_perfect"] += 1
            continue

        # Tier 3: Perfect Monologue (3-4s + dot)
        segments = find_suitable_sentence(mono_dir, spk, "monologue", 3.0, 4.0, True) if mono_dir.exists() else []
        if segments:
            prefix = segments[0]['wav_path'].stem.rsplit('_', 1)[0]
            merge_segments(prefix, segments, output_dir, "monologue_perfect")
            stats["monologue_perfect"] += 1
            continue

        # Tier 4: Flexible Readtext (2-6s, no dot)
        segments = find_suitable_sentence(read_dir, spk, "readtext", 2.0, 6.0, False) if read_dir.exists() else []
        if segments:
            prefix = segments[0]['wav_path'].stem.rsplit('_', 1)[0]
            merge_segments(prefix, segments, output_dir, "flexible_readtext")
            stats["flexible"] += 1
            continue

        # Tier 5: Flexible Monologue (2-6s, no dot)
        segments = find_suitable_sentence(mono_dir, spk, "monologue", 2.0, 6.0, False) if mono_dir.exists() else []
        if segments:
            prefix = segments[0]['wav_path'].stem.rsplit('_', 1)[0]
            merge_segments(prefix, segments, output_dir, "flexible_monologue")
            stats["flexible"] += 1
            continue

        # Tier 6: Final Fallback - Any segment at all
        any_found = False
        for d, pattern in [(read_dir, "readtext"), (mono_dir, "monologue"), (sent_dir, "sentence")]:
            if not d.exists(): continue
            wavs = sorted(list(d.glob(f"{spk}_*_{pattern}_*.wav")))
            if wavs:
                wav_path = wavs[0]
                txt_path = wav_path.with_suffix('.txt')
                csv_path = wav_path.with_suffix('.csv')
                if txt_path.exists() and csv_path.exists():
                    prefix = wav_path.stem.rsplit('_', 1)[0]
                    merge_segments(prefix, [{'wav_path': wav_path, 'txt_path': txt_path, 'csv_path': csv_path, 'sr': get_sampling_rate(wav_path)}], output_dir, "final_fallback")
                    stats["flexible"] += 1
                    any_found = True
                    break
        
        if not any_found:
            logger.error(f"FATAL: No reference audio for speaker {spk} after all fallbacks.")
            stats["failed"] += 1

    logger.info(f"Summary: {stats}")

if __name__ == "__main__":
    main()
