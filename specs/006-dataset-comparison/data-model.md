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

## Output Structures (CSV)

### 1. Data Integrity (`comparison_integrity.csv`)
| Column | Type | Description |
|--------|------|-------------|
| task | string | Task group |
| speaker_id | string | Speaker ID |
| filename | string | File name |
| exists_in_test | bool | Audio file parallelism |
| csv_exists_in_test | bool | Alignment CSV parallelism |
| emb_exists_in_ref | bool | Reference embedding presence |
| emb_exists_in_test | bool | Test embedding presence |
| transcription_match | bool | Character-level TXT match |
| status | string | HC or PD |

### 2. Speaker Embedding Summary (`speaker_embedding_summary.csv`)
Aggregated distance metrics per speaker and task.
| Column | Type | Description |
|--------|------|-------------|
| speaker_id | string | Speaker ID |
| task | string | Task group |
| avg_cos_dist | float | Mean Cosine distance |
| std_cos_dist | float | Std Dev Cosine distance |
| avg_euc_dist | float | Mean Euclidean distance |
| std_euc_dist | float | Std Dev Euclidean distance |
| status | string | HC or PD |

### 3. Detailed Embeddings (`comparison_embeddings.csv`)
Individual sentence-level distances.
| Column | Type | Description |
|--------|------|-------------|
| speaker_id | string | Speaker ID |
| filename | string | Source WAV filename |
| task | string | Task group |
| cosine_distance | float | Individual pair Cosine distance |
| euclidean_distance | float | Individual pair Euclidean distance |
| status | string | HC or PD |

## Validation Rules
1. **Filename Matching**: Test files must have exactly the same name as reference files.
2. **Transcription Identity**: `.txt` files must be character-identical (ignoring leading/trailing whitespace).
3. **Phoneme Alignment**: Comparison only occurs if the phoneme sequences (MAU/ORT) match in order; otherwise, mark as "Alignment Mismatch".
4. **Outlier Filtering**: Use Z-score > 3 to filter extreme phoneme duration deltas before averaging.
