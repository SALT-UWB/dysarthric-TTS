# Data Model: segment-pcgita-sentences

## Entity: Segment

Represents a single sentence or pause-delimited audio unit extracted from a long recording.

### Properties

| Field | Type | Description |
|-------|------|-------------|
| `segment_id` | String | Format: `<original_stem>_###` (e.g., `001PD_S1_readtext_005`) |
| `start_samples` | Integer | Absolute sample index in the source file where this segment begins. |
| `end_samples` | Integer | Absolute sample index in the source file where this segment ends. |
| `duration_sec` | Float | Calculated as `(end - start) / sampling_rate`. |
| `transcript` | String | Plain text extracted from ORT tokens. |
| `phonemes` | List[Row] | Filtered CSV rows corresponding to this segment with shifted timing. |

### Constraints

- `start_samples < end_samples`
- `end_samples <= source_audio_total_samples`
- Metadata rows MUST be shifted such that the first row of a segment has a relative `BEGIN` reflecting its position within the segment (usually 0 if starting at the very beginning of the audio slice).
