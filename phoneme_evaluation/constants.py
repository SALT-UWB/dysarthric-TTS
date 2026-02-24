from pathlib import Path

# Absolute path to the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Base Paths
DATA_ROOT = PROJECT_ROOT / "datalocal" / "PC-GITA_v260210_24kHz"
METADATA_PATH = DATA_ROOT / "_metadata" / "PCGITAtoPD_mapping.csv"

# Directories to be processed
TASKS = [
    "ddk",
    "monologue_split",
    "readtext_split",
    "sentences_cleaned",
    "words_merged"
]

# Technical and non-phonemic markers to be filtered by default
TECHNICAL_TOKENS = ["<p:>", "<usb>", "sil", "sp", "SIL", "SP"]

# Groups for analysis
GROUPS = ["HC", "PD"]
SEXES = ["M", "F"]

# Alignment CSV Format
SAMPLING_RATE = 24000
