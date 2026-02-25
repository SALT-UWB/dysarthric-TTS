import argparse
import logging
import sys
from pathlib import Path
from typing import Any

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
    info = sf.info(str(wav_path))
    return info.frames / info.samplerate

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
        # Audio
        audio, _ = sf.read(str(seg['wav_path']))
        all_audio.append(audio)
        
        # Text
        with open(seg['txt_path'], 'r', encoding='utf-8') as f:
            txt = f.read().strip()
            all_txt_segments.append(txt)
        
        # CSV (Alignment)
        df = pd.read_csv(seg['csv_path'], sep=csv_delimiter)
        
        # Shift timings
        df['BEGIN'] = df['BEGIN'] + current_offset_samples
        
        # Shift TOKEN IDs
        if 'TOKEN' in df.columns:
            max_token_in_seg = df['TOKEN'].max()
            df.loc[df['TOKEN'] >= 0, 'TOKEN'] = df.loc[df['TOKEN'] >= 0, 'TOKEN'] + current_token_offset
            if max_token_in_seg >= 0:
                current_token_offset += (int(max_token_in_seg) + 1)
        
        all_csv.append(df)
        current_offset_samples += len(audio)

    # Finalize
    merged_audio = np.concatenate(all_audio)
    merged_txt = " ".join(all_txt_segments)
    merged_csv = pd.concat(all_csv, ignore_index=True)
    
    if source_name == "sentences":
        merged_stem = f"{speaker_id}_sentences_5_6"
    else:
        # Extract segment IDs (last part of stem, e.g., 001 from prefix_001)
        segment_ids = "_".join([seg['wav_path'].stem.split('_')[-1] for seg in segments])
        merged_stem = f"{speaker_id}_{segment_ids}"
    
    sf.write(str(output_dir / f"{merged_stem}.wav"), merged_audio, sr)
    with open(output_dir / f"{merged_stem}.txt", 'w', encoding='utf-8') as f:
        f.write(merged_txt)
    merged_csv.to_csv(output_dir / f"{merged_stem}.csv", sep=csv_delimiter, index=False)
    
    logger.info(f"Generated speaker reference for {speaker_id} from {source_name} ({len(segments)} segments)")

def collect_duration_target(
    input_dir: Path, 
    speaker_id: str, 
    pattern: str, 
    min_sec: float = 6.0, 
    max_sec: float = 8.0
) -> list[dict[str, Any]]:
    """Collects segments until target duration is reached."""
    wavs = sorted(list(input_dir.glob(f"{speaker_id}_*_{pattern}_*.wav")))
    if not wavs:
        return []
    
    segments = []
    current_dur = 0.0
    
    for wav_path in wavs:
        dur = get_duration_sec(wav_path)
        txt_path = wav_path.with_suffix('.txt')
        csv_path = wav_path.with_suffix('.csv')
        
        if not (txt_path.exists() and csv_path.exists()):
            continue
            
        segments.append({
            'wav_path': wav_path,
            'txt_path': txt_path,
            'csv_path': csv_path,
            'sr': get_sampling_rate(wav_path)
        })
        current_dur += dur
        
        if current_dur >= min_sec:
            break
            
    return segments

def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare speaker reference audio.")
    parser.add_argument("--base_dir", type=str, default="datalocal/PC-GITA_v260210_24kHz")
    parser.add_argument("--output_dir", type=str, default="datalocal/PC-GITA_v260210_24kHz/speakers_ref_sentences")
    args = parser.parse_args()
    
    base_dir = Path(args.base_dir)
    sent_dir = base_dir / "sentences_cleaned"
    read_dir = base_dir / "readtext_split"
    mono_dir = base_dir / "monologue_split"
    output_dir = ensure_dir(args.output_dir)
    
    # 1. Identify all speakers from all sources
    all_wavs = list(sent_dir.glob("*.wav")) + list(read_dir.glob("*.wav")) + list(mono_dir.glob("*.wav"))
    all_speakers = sorted(list(set(w.name.split('_')[0] for w in all_wavs)))
    
    logger.info(f"Found {len(all_speakers)} total speakers across all sources.")
    
    stats = {"sentences": 0, "readtext": 0, "monologue": 0, "failed": 0}
    
    for spk in all_speakers:
        # Try primary source: sentences_cleaned (S5 + S6)
        s5_wavs = sorted(list(sent_dir.glob(f"{spk}_*_sentence5_*.wav")))
        s6_wavs = sorted(list(sent_dir.glob(f"{spk}_*_sentence6_*.wav")))
        
        if s5_wavs and s6_wavs:
            segments = []
            for wav_path in (s5_wavs + s6_wavs):
                txt_path = wav_path.with_suffix('.txt')
                csv_path = wav_path.with_suffix('.csv')
                if txt_path.exists() and csv_path.exists():
                    segments.append({'wav_path': wav_path, 'txt_path': txt_path, 'csv_path': csv_path, 'sr': get_sampling_rate(wav_path)})
            
            if segments:
                # Get the speaker session prefix (e.g. 001PD_S1) from first segment
                prefix = segments[0]['wav_path'].stem.rsplit('_', 2)[0]
                merge_segments(prefix, segments, output_dir, "sentences")
                stats["sentences"] += 1
                continue

        # Try Tier 2: readtext_split (6-8s)
        segments = collect_duration_target(read_dir, spk, "readtext", 6.0, 8.0)
        if segments:
            prefix = segments[0]['wav_path'].stem.rsplit('_', 1)[0]
            merge_segments(prefix, segments, output_dir, "readtext")
            stats["readtext"] += 1
            continue

        # Try Tier 3: monologue_split (6-8s)
        segments = collect_duration_target(mono_dir, spk, "monologue", 6.0, 8.0)
        if segments:
            prefix = segments[0]['wav_path'].stem.rsplit('_', 1)[0]
            merge_segments(prefix, segments, output_dir, "monologue")
            stats["monologue"] += 1
            continue
            
        logger.warning(f"Could not find reference audio for speaker {spk}")
        stats["failed"] += 1

    logger.info(f"Summary: {stats}")

if __name__ == "__main__":
    main()
