# MidNet News Production Orchestrator

## Purpose

Produce a reviewable, auditable MidNet News package from the files in `input/`. The orchestrator validates the brief, generates or accepts subtitles, inventories only supplied visuals, makes three distinct thumbnail comps, renders a draft, runs technical checks, and packages final-named media only after the QC gate passes.

## Hard requirements

1. Preserve the supplied MidNet News logo exactly. Never redraw, recolor, crop, remove background from, or otherwise edit the original. Use only the approved transparent PNG at `brand/logo/midnet-news-logo-hd.png` (or the documented input copy).
2. Do not invent news facts, quotes, captions, source/license claims, asset identity, or approval. Never use a visually plausible but unverified image as a real event/person.
3. Treat `input/src/` items as unreviewed until the user supplies an explicit `asset-review.json` attestation. Record origin, source URL and license. Public availability is not a reuse license.
4. Keep exact source audio, English script and generated transcript distinguishable. Never change spoken words to match the script without an editor's review. The script can help identify likely recognition errors, not prove what was said.
5. Final names are gated. `NEEDS_REVIEW` means do not publish or rename drafts to final deliverables. Never write a PASS approval on the user's behalf.
6. Use the configured 16:9 1920x1080, 30 fps, navy/white/red system; respect safe margins. Captions must be legible, no more than two lines, and not compete with headlines/logo.
7. No network asset search or downloads happen in v0.1. If a source is missing, report it and request editor-supplied, reviewed media rather than silently substituting.

## Input contract

`input/` contains exactly one `audio.mp3` or `audio.wav`, `brief.md`, optional `subtitles.srt`, optional `src/` visuals, and optional review JSON files. `brief.md` must provide English Full News, three titles, three thumbnail ideas, resource names, and a YouTube description. Target description length is 800–1000 characters.

## Execution

Run `midnet produce --input ./input --output ./production` from repo root. If SRT is absent, install and use optional local `faster-whisper`; never fabricate timing. Inspect `workspace/drafts/`, `workspace/render-error.txt`, the manifest, and the report. Fix problems in input/config and rerun. Ask a human editor to do required editorial and rights checks; the human—not the agent—owns `input/qc-approval.json`.

## Specialist contracts

Read the matching contract before changing a stage:

- `skills/audio-to-srt/SKILL.md`
- `skills/visual-resource-manager/SKILL.md`
- `skills/news-video-planner/SKILL.md`
- `skills/motion-graphics/SKILL.md`
- `skills/youtube-thumbnail-design/SKILL.md`
- `skills/video-qc/SKILL.md`
- `skills/final-packager/SKILL.md`

## Current implementation scope

The executable v0.1 implements input validation, structured brief parsing, optional local ASR or supplied SRT, user-asset manifest/source record, static card/thumbnail rendering with Pillow, FFmpeg assembly, technical decode/probe and a human approval gate. It does not implement automatic licensed visual discovery, identity/event verification, Remotion motion design, source-image association to individual narration claims, ASR/script forced alignment, automatic black-frame/loudness/subtitle-sync analysis, or AI factual checking. Clearly disclose these limitations; do not present the architecture plan as a working feature.
