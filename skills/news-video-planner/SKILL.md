# News Video Planner Contract

**Purpose:** connect narration timeline to verified assets and an editorially coherent scene plan.

- **Inputs:** English Full News, subtitle cue timings, approved asset manifest, brand/render configuration.
- **Process:** divide story into claims/scene beats; map each beat to a specifically verified visual; plan title/lower-third/map/stat cards only when facts are sourced; track archive/illustrative labels; avoid unjustified repetition; protect the logo and captions with safe zones.
- **Outputs:** proposed `timeline.json` with time range, narration, source asset IDs, text, treatment, evidence/source references and review state.
- **Validation:** every documentary asset is mapped to a specific claim and source; every on-screen factual claim appears in source brief; time ranges are contiguous/non-overlapping and within audio duration.
- **Failure:** no suitable source, uncertain mapping or insufficient evidence → neutral title card or hold for editor; never guess.

**v0.1 status:** this contract is documented; a scene timeline planner and claim-level source matching are not yet implemented. Current renderer creates timed static cards from subtitle cues and uses only user-approved images.