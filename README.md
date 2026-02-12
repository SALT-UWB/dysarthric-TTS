# FAU dysarthric-TTS (PC-GITA)

Preprocessing and synthetic speech training for healthy vs dysarthric speakers using the PC-GITA dataset.

## Setup Instructions

This project uses a local Python virtual environment.

### 1. Create the environment
```powershell
python -m venv .venv
```

### 2. Activate the environment
- **Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- **Linux/macOS:**
  ```bash
  source .venv/bin/activate
  ```

### 3. Install dependencies
```bash
pip install -e .
# Or manually:
pip install librosa pandas soundfile pytest ruff mypy jupyter nbformat nbconvert
```

## Dataset Protection

**CRITICAL**: NEVER commit real PC-GITA audio, transcripts, or metadata to this repository. All raw data should be stored in `datalocal/` which is ignored by git.

The repository includes a minimal synthetic dummy dataset in `tests/data_prepare/dummy_data/` for CI and testing.
