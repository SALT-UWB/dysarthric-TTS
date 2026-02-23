# Data Model: wavLM-evaluation

## Entities

### EmbeddingFile
- **Path**: Absolute path to `.pt` file.
- **SpeakerID**: Unique identifier (e.g., `001PD`).
- **HealthStatus**: `PD` or `HC` (extracted from SpeakerID).
- **Session**: e.g., `S1`.
- **Group**: One of `ddk`, `monologue`, `readtext`, `sentence`, `words`.
- **Vector**: Torch tensor of shape `(D,)`.

### Centroid
- **Type**: `Group` or `Speaker`.
- **SpeakerID**: Associated speaker.
- **GroupID**: Associated group (if Type=Group).
- **Vector**: Mean vector of constituent embeddings.

### DistanceRecord
- **SourceID**: ID of the sample or centroid being measured.
- **TargetID**: ID of the reference centroid or neighbor.
- **Metric**: Cosine Distance.
- **Value**: Float [0, 2].

## Relationships
- **Speaker** HAS MANY **Groups**.
- **Group** HAS MANY **EmbeddingFiles**.
- **Speaker** HAS ONE **GlobalCentroid**.
- **Group** HAS ONE **GroupCentroid**.

## Validation Rules
- All embeddings MUST have the same dimensionality.
- Speaker ID MUST match the project's naming convention (3 digits + status).
- Health status MUST be binary (PD/HC).
