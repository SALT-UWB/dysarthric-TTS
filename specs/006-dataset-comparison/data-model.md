# Data Model: Dataset Comparison

## Entities

### ComparisonSample
Represents a pair of parallel recordings (Reference vs Test).
- **SpeakerID**: string (e.g., "001PD")
- **TaskGroup**: string (ddk, monologue, readtext, sentences, words)
- **FileName**: string
- **AudioDurationDelta**: float (seconds)
- **TranscriptionMatch**: boolean
- **EmbeddingDistance**: float (Cosine distance)
- **PhonemeDeltas**: Map<Phoneme, float>
- **MissingPhonemes**: List<Phoneme>

### SpeakerComparisonSummary
Aggregated metrics for a single speaker.
- **SpeakerID**: string
- **Status**: enum (PD, HC)
- **AvgEmbeddingDistance**: float
- **AvgPhonemeDurationDelta**: float
- **MissingPhonemeCount**: int

## Validation Rules
1. **Filename Matching**: Test files must have exactly the same name as reference files.
2. **Transcription Identity**: `.txt` files must be character-identical (ignoring leading/trailing whitespace).
3. **Phoneme Alignment**: Comparison only occurs if the phoneme sequences (MAU/ORT) match in order; otherwise, mark as "Alignment Mismatch".
4. **Outlier Filtering**: Use Z-score > 3 to filter extreme phoneme duration deltas before averaging.
