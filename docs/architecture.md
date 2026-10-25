# Workflow and release architecture

```text
input package
   ├── brief parser + audio validation
   ├── Audio-to-SRT (provided SRT or optional local ASR)
   ├── visual inventory + source record (no automatic remote collection)
   ├── thumbnail comps (three distinct treatments)
   ├── static scene-card assembly + caption burn-in (FFmpeg)
   └── technical QC + explicit human editorial approval
           ├── NEEDS_REVIEW → keep drafts in workspace/drafts
           └── PASS → promote final-named deliverables to production/
```

## Data flow contracts

| Stage | Inputs | Outputs | Release gate |
|---|---|---|---|
| Input validation | audio, brief | parsed story metadata | exactly one MP3/WAV, script, 3 titles, 3 thumbnail concepts, description |
| Audio-to-SRT | audio, optional SRT, English script reference | SRT, transcript, timing JSON | valid cues; no synthetic timings |
| Visual inventory | resource list, `src/`, optional review JSON | asset manifest, source record | asset remains ineligible until explicit attestation |
| Thumbnail design | ideas, titles, approved source images, logo | 3 1280×720 draft PNGs | layout variants differ; factual review required |
| Motion renderer | audio, SRT, approved images, logo, config | draft MP4 | FFmpeg output and full decode; v0.1 is static scene cards |
| QC | draft assets, metadata, source logs | `productionReport.json` | technical blockers plus explicit human attestations |
| Packager | PASS report and draft files | final package | never promotes on NEEDS_REVIEW |

## Intentional safety decisions

- Remote image search/downloading is not implemented. Automated collection can create false context and licensing risk; provide a verified licensed asset and record its source/license.
- There is no original MidNet logo or approved typeface in the repository. Do not fabricate one or silently substitute a white-background logo. Production QC requires the supplied transparent original logo.
- No user-facing factual claim is auto-certified. The CLI is a deterministic local scaffold, not a newsroom editor or fact-checker.
- The system doesn't use external API keys or send unpublished scripts/audio to a third-party service. Optional faster-whisper runs locally, subject to its model package and local compute.

## Next implementation increments

1. Add a claim/visual planner with explicit per-scene source mapping and no round-robin imagery.
2. Add licensed visual source integrations only with a vetted catalog, rights metadata and editor review.
3. Move rendering to a Remotion timeline and add tested camera movement, transition/lower-third templates and branding overlays.
4. Add audio loudness, clipping, black/frozen frame, SRT/audio alignment and mobile-size thumbnail analysis.
5. Add structured retry/resume state and checksummed, reproducible production bundles.

Each increment should preserve the same input/output contracts and failing-closed release gate.
