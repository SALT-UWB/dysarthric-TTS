from pathlib import Path

import soundfile as sf


def get_sampling_rate(wav_path: Path | str) -> int:
    """Reads the sampling rate from a WAV file header."""
    info = sf.info(str(wav_path))
    return int(info.samplerate)

def get_duration_samples(wav_path: Path | str) -> int:
    """Reads the total number of samples from a WAV file header."""
    info = sf.info(str(wav_path))
    return int(info.frames)
