# Research: segment-pcgita-sentences

## Audio Splitting Strategy

- **Decision**: Use `librosa` for reading WAV metadata (sampling rate) and `soundfile` for writing segments to ensure sample-accurate cuts without unintended re-encoding artifacts.
- **Rationale**: `librosa` is industry standard for analysis, while `soundfile` provides lower-level sample access suitable for precise segmentation.
- **Alternatives considered**: `pydub` (rejected due to dependency on ffmpeg and less precise sample handling).

## Alignment Midpoint Logic

- **Decision**: All segment cuts will occur exactly at the midpoint of the pause interval in samples: `cut_sample = row['BEGIN'] + (row['DURATION'] // 2)`.
- **Rationale**: Minimizes the risk of clipping the end of the previous word or the start of the next word, providing a natural buffer for silence.

## Metadata Shifting

- **Decision**: Segmented CSVs will have their `BEGIN` column updated using: `new_begin = old_begin - segment_start_samples`.
- **Rationale**: Ensures that individual segments are self-contained and ready for downstream training pipelines that expect 0-indexed timing.

## Notebook Validation

- **Decision**: The Jupyter notebook will use `pandas` to aggregate stats and `pathlib` for robust cross-platform path validation.
- **Rationale**: Standard Python data science stack ensures maintainability.
