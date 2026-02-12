<!--
Sync Impact Report:
- Version change: 1.0.0 -> 1.1.0
- List of modified principles:
  - Engineering Quality (Principle V) -> Added requirement for .gitignore of raw data.
- Added sections: None
- Removed sections: None
- Templates requiring updates:
  - .specify/templates/tasks-template.md: ✅ Added placeholder for dummy data setup.
  - .specify/templates/spec-template.md: ✅ Added Ethics & Licensing section.
  - .specify/templates/plan-template.md: ✅ Updated Constitution Check section.
  - .gemini/commands/speckit.constitution.toml: ✅ Removed CLAUDE reference and corrected paths.
- Follow-up TODOs: None
-->

# FAU dysarthric-TTS (PC-GITA) Constitution

## Core Principles

### I. Dataset Licensing & Access
The project MUST strictly respect the licensing and access terms of the PC-GITA dataset.
- Real dataset audio, transcripts, or metadata MUST NEVER be redistributed or committed to the repository.
- The repository MUST be capable of running all tests and examples using a minimal synthetic or dummy sample dataset.
- Access to the raw dataset MUST be managed externally; the codebase SHALL assume the data is present in a specific ignored directory (e.g., `datalocal/raw`).

### II. Privacy & Ethics
Voice data MUST be treated as highly sensitive personal information.
- Re-identification of participants MUST NOT be attempted.
- The project SHALL NOT implement features for voice cloning or identity reproduction of PC-GITA participants.
- All documentation and outputs MUST avoid any claims of mimicking real participants.

### III. Deterministic Preprocessing
Preprocessing of the dataset MUST be fully deterministic and repeatable.
- All random processes (e.g., splits) MUST use fixed seeds.
- Preprocessing configurations MUST be logged or versioned alongside the data.
- The environment (dependencies, Python version) MUST be captured (e.g., via `pyproject.toml` or `requirements.txt`).
- Preprocessing steps MUST include "fail-loud" validation to catch anomalies in the raw data early.

### IV. Normalized Source of Truth
The project MUST define a single canonical format for the normalized output.
- All audio MUST be converted to a standard format (e.g., 16kHz, mono, WAV).
- Metadata MUST adhere to a strict, versioned schema (e.g., JSON or CSV manifest).
- Every processed batch MUST include a manifest with integrity checks (e.g., checksums).
- Data splits (train/val/test) MUST be deterministic and recorded.
- Processed outputs MUST be versioned (e.g., `data/processed/v1`).

### V. Engineering Quality
Implementation MUST follow high engineering standards.
- Production logic MUST be encapsulated in importable Python modules; notebooks are restricted to exploration and visualization.
- Code MUST be linted and type-checked using `ruff` and `mypy`.
- Automated testing with `pytest` is MANDATORY for all preprocessing logic.
- CI pipelines MUST run on all Pull Requests to enforce quality gates.
- The repository MUST maintain a clean structure with clear documentation.
- Raw data directories MUST be strictly ignored via `.gitignore`.

### VI. Governance & Change Management
The Constitution is the supreme document and MUST override any feature specification, implementation plan, or task list.
- Any change to the normalized data format or strict schema MUST trigger a MINOR or MAJOR version bump of the processed dataset.
- Versioning of the Constitution itself MUST follow semantic versioning rules (MAJOR: principle removals/redefinitions, MINOR: new principles, PATCH: clarifications).
- Changes to core principles require an amendment record and migration notes for affected artifacts.

## Governance
All development activities must align with the core principles. The amendment process requires documenting the rationale for any changes and assessing the impact on existing data and code.

**Version**: 1.1.0 | **Ratified**: 2026-02-11 | **Last Amended**: 2026-02-12
