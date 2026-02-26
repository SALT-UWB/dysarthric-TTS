from pathlib import Path

# Paths
DATA_ROOT = Path("datalocal")
METADATA_PATH = DATA_ROOT / "PC-GITA_v260210_24kHz" / "_metadata" / "PCGITAtoPD_mapping.csv"
REPORTS_DIR = Path("reports")

# Evaluation Tasks
TASKS = ["ddk", "monologue_split", "readtext_split", "sentences_cleaned", "words_merged"]

# Comparison Thresholds
DURATION_RELATIVE_THRESHOLD = 0.50  # 50% difference
COSINE_DISTANCE_THRESHOLD = 0.2  # Arbitrary initial threshold for alerts

# Audio Parameters
SAMPLING_RATE = 24000  # Default for PC-GITA v260210
