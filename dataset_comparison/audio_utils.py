import soundfile as sf
import logging
from pathlib import Path
from typing import Optional, Tuple
from .constants import DURATION_RELATIVE_THRESHOLD

logger = logging.getLogger(__name__)

def get_audio_duration(file_path: Path) -> float:
    """
    Returns duration of audio file in seconds.
    """
    try:
        with sf.SoundFile(file_path) as f:
            return len(f) / f.samplerate
    except Exception as e:
        logger.error(f"Error reading duration for {file_path.name}: {e}")
        return 0.0

def compare_durations(ref_path: Path, test_path: Path) -> Tuple[float, bool]:
    """
    Calculates duration delta and returns (delta, is_significant).
    Significant is defined as > 25% difference relative to reference length.
    """
    ref_dur = get_audio_duration(ref_path)
    test_dur = get_audio_duration(test_path)
    
    if ref_dur == 0:
        return 0.0, False
        
    delta = abs(ref_dur - test_dur)
    relative_diff = delta / ref_dur
    
    is_significant = relative_diff > DURATION_RELATIVE_THRESHOLD
    
    if is_significant:
        logger.warning(
            f"Significant duration delta for {ref_path.name}: "
            f"Ref={ref_dur:.3f}s, Test={test_dur:.3f}s (Diff={relative_diff:.1%})"
        )
    
    return delta, is_significant
