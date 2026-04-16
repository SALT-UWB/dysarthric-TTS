# Plan 005: Speaker Reference Generation

## Implementation Phases

### Phase 1: Tiered Logic Development
1. **Identify Speakers**: Iterate over all available speakers (100 in total).
2. **Primary (Tier 1)**: Search `sentences_cleaned` for `sentence5_001` and `sentence6_001`.
3. **Fallback (Tier 2/3)**: Implement `collect_duration_target` to gather split segments from Readtext or Monologue until a duration threshold (6-8s) is reached.

### Phase 2: Data Merging & Preservation
1. **WAV**: Use `soundfile` and `numpy` to concatenate audio.
2. **TXT**: Concatenate strings with space.
3. **CSV**: Offset `BEGIN` (timing) and `TOKEN` (word identifier) values to maintain data consistency.

### Phase 3: Integration
1. **Default Paths**: Set defaults to the current PC-GITA corpus version.
2. **Verification**: Verify triplets are created for all 100 speakers.
