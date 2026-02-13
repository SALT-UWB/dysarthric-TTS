import json
from pathlib import Path
from typing import Any

from data_prepare.audio_utils import get_duration_samples, get_sampling_rate

def validate_triples(data_dir: Path | str) -> dict[str, Any]:
    """
    Validates that every stem has a matching .wav, .txt, and .csv file.
    Returns a dict with 'valid_stems' and 'missing_files'.
    """
    data_dir = Path(data_dir)
    wavs = set(f.stem for f in data_dir.glob("*.wav"))
    txts = set(f.stem for f in data_dir.glob("*.txt"))
    csvs = set(f.stem for f in data_dir.glob("*.csv"))
    
    all_stems = wavs | txts | csvs
    valid_stems = []
    missing_files = []
    
    for stem in sorted(all_stems):
        missing = []
        if stem not in wavs:
            missing.append(".wav")
        if stem not in txts:
            missing.append(".txt")
        if stem not in csvs:
            missing.append(".csv")
        
        if not missing:
            valid_stems.append(stem)
        else:
            missing_files.append({"stem": stem, "missing": missing})
            
    return {
        "valid_stems": valid_stems,
        "missing_files": missing_files,
        "total_stems": len(all_stems)
    }

def compute_statistics(data_dir: Path | str, stems: list[str]) -> dict[str, Any]:
    """
    Computes dataset statistics for the given stems.
    """
    data_dir = Path(data_dir)
    stats: dict[str, dict[str, Any]] = {
        "total": {"files": 0, "sentences": 0, "words": 0, "duration_sec": 0.0},
        "hc": {"files": 0, "sentences": 0, "words": 0, "duration_sec": 0.0},
        "pd": {"files": 0, "sentences": 0, "words": 0, "duration_sec": 0.0}
    }
    
    # Tracking original source files (by removing the _### suffix)
    source_files = set()
    hc_sources = set()
    pd_sources = set()
    
    for stem in stems:
        # Categorize
        is_hc = "YHC" in stem.upper() or "EHC" in stem.upper()
        is_pd = "PD" in stem.upper() and not is_hc
        
        group = "hc" if is_hc else "pd" if is_pd else None
        
        # Read word count from TXT
        txt_path = data_dir / f"{stem}.txt"
        with open(txt_path, encoding='utf-8') as f:
            content = f.read()
            words = len(content.split())
            
        # Get duration
        wav_path = data_dir / f"{stem}.wav"
        sr = get_sampling_rate(wav_path)
        samples = get_duration_samples(wav_path)
        duration = float(samples) / sr

        stats["total"]["sentences"] += 1
        stats["total"]["words"] += words
        stats["total"]["duration_sec"] += duration
        
        source_stem = stem.rsplit('_', 1)[0] if '_' in stem else stem
        source_files.add(source_stem)
        
        if group:
            stats[group]["sentences"] += 1
            stats[group]["words"] += words
            stats[group]["duration_sec"] += duration
            if is_hc:
                hc_sources.add(source_stem)
            else:
                pd_sources.add(source_stem)
            
    stats["total"]["files"] = len(source_files)
    stats["hc"]["files"] = len(hc_sources)
    stats["pd"]["files"] = len(pd_sources)
    
    return stats

def save_report(stats: dict[str, Any], output_path: Path | str) -> None:
    """Saves statistics to a JSON file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=4)
