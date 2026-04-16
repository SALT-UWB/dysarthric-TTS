# Tasks 005: Speaker Reference Generation

- [x] Analyze availability of speakers across cleaned sentences, readtext, and monologue.
- [x] Map speaker IDs and task sessions.
- [x] Create the tiered selection script `speaker_reference.py`.
- [x] Implement tiered selection logic:
  - [x] Primary: Sentences 5 & 6 (all segments).
  - [x] Fallback 1: Readtext (6-8s).
  - [x] Fallback 2: Monologue (6-8s).
- [x] Correctly handle CSV shifts (timing and tokens).
- [x] Implement descriptive naming for fallbacks (segment IDs).
- [x] Generate reference files for 100 speakers.
- [x] Verify total counts (84 sentences, 14 readtext, 2 monologue).
- [x] Push script and documentation to the repository.
