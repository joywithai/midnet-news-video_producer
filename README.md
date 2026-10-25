# MidNet News Video Producer

A local-first, auditable production workflow for MidNet News. It turns a structured `brief.md`, one English narration recording, reviewed visual assets, and a transparent brand logo into **draft** captions, thumbnails, and a 16:9 H.264/AAC news video. It withholds final-named production media until technical checks pass and a named human reviewer explicitly approves editorial, rights, subtitle, and thumbnail checks.

> **Current release: v0.1 foundation.** The CLI, brief parser, optional local Whisper transcription, asset inventory, branded graphic generation, FFmpeg render, source record, and QC gate are implemented. This version does not automatically browse for/download third-party photos, prove a visual's identity or license, perform frame-accurate script alignment, generate rich Remotion motion graphics, or replace a human editor. Those are deliberate safety boundaries, not claims of completed automation. Unreviewed or unverifiable outputs remain `NEEDS_REVIEW`.

## Requirements

- Python 3.10+
- FFmpeg **and** FFprobe on `PATH` for rendering and media audit
- Pillow (installed by the project)
- Optional: `faster-whisper` for local speech transcription (`pip install -e '.[asr]'`). The first model run may download model files; choose a model/device suitable for your machine.
- One audio file (`audio.mp3` or `audio.wav`) and `brief.md`

Install:

```bash
python -m venv .venv
. .venv/bin/activate                 # Windows: .venv\\Scripts\\activate
python -m pip install -e .           # or: python -m pip install -e '.[asr]'
ffmpeg -version && ffprobe -version
```

## Input package

```text
input/
├── audio.mp3                         # exactly one audio.mp3 or audio.wav
├── brief.md
├── subtitles.srt                     # optional; otherwise local faster-whisper is required
├── asset-review.json                 # optional approvals for user-provided visuals
├── qc-approval.json                  # optional, completed by a human after reviewing drafts
├── src/                               # source images; unreviewed by default
└── brand/logo/midnet-news-logo-hd.png # optional copy of the original transparent logo
```

Required `brief.md` headings are case-insensitive (English script heading may be `English Full News`, `Full News`, `News Script`, or `Script`):

```markdown
# English Full News
Write the complete spoken English news script here.

# Photo / Resource Names
- City hall exterior (source/date required)
- Official document cover

# Thumbnail Ideas
1. City hall with a short headline treatment
2. Document detail with a different composition
3. Map-led explainer concept

# Titles
1. First accurate YouTube title
2. Second accurate YouTube title
3. Third accurate YouTube title

# Description
An accurate 800–1000 character YouTube description.
```

Exactly three titles and three ideas are required. The description is checked against the requested 800–1000 character range; out-of-range descriptions are flagged for review. Keep thumbnail concept descriptions factual. Put any literal thumbnail copy in the idea itself (recommended: `Text: ...; visual: ...`).

### Approving supplied visuals

Nothing in `src/` is automatically treated as factually relevant or rights-cleared. Review every file and add its filename to `input/asset-review.json` only when appropriate:

```json
{
  "assets": [
    {
      "path": "city-hall.jpg",
      "approved": true,
      "source_url": "https://publisher.example/story/photo",
      "license": "CC BY 4.0; attribution required",
      "notes": "City hall exterior, verified for the reported event/date; attribution: Photographer Name"
    }
  ]
}
```

This is a **user attestation**, not independent verification. Never use an image of an unverified person, place, event, document, or logo as if it depicts the news. Archival images should be labeled in the notes and in the finished editorial review. This release does not fetch remote assets: do not assume that a search result or publicly viewable image is reusable.

### The logo and fonts

Place the supplied **original**, background-removed transparent PNG at `brand/logo/midnet-news-logo-hd.png`. The supplied original artwork is retained at `brand/logo/source-original.jpg`; its exterior white background has been removed into `brand/logo/midnet-news-logo-hd.png` without changing the design. The transparent PNG is 1200×1200 (upscaled from the supplied 600×600 JPEG). The project does not redraw or recolor it. If the asset is missing in another checkout, graphics are still generated as drafts, but QC blocks final delivery. See `brand/logo/README.md`. Fonts are not bundled; commercial-use licenses must be confirmed before placing licensed font files under `brand/fonts/`. System DejaVu Sans is only a development fallback, not a claim of a licensed broadcast font. Defaults are in `config/production.json`, `brand/theme/colors.json` and `brand/theme/typography.json`.

## Run

From the repository root:

```bash
midnet produce --input ./input --output ./production
# or, without installing the console command:
python -m midnet_news.cli produce --input ./input --output ./production
```

For an existing SRT, put it at `input/subtitles.srt`. Otherwise install the ASR extra; transcription without that dependency fails closed rather than inventing subtitle timings. Transcription uses the recording as spoken and preserves segment timestamps. The brief script is an editorial reference and is **not** silently substituted for words actually spoken.

### Draft/final behavior

- Intermediate renders and thumbnail comps live in `workspace/drafts/`.
- `production/sourceRecord.txt` and `production/productionReport.json` are created for every completed run.
- Draft assets are not promoted to `newsVideo.mp4`, `subtitles.srt`, `newsThumbnail1.png`–`3.png`, and `uploadInfo.txt` until blocking automated checks pass **and** `input/qc-approval.json` contains named human attestations for all required checks.
- The default result is `NEEDS_REVIEW` (CLI exit code 2). This is intentional. Do not publish drafts directly.

After reviewing the draft video, all three thumbnail drafts, captions against audio, visual identity/event accuracy, rights/source records, scene sequence and audio quality, create:

```json
{
  "approved": true,
  "reviewer": "Editor name",
  "subtitle_sync": true,
  "visual_accuracy": true,
  "thumbnail_accuracy": true,
  "copyright_review": true,
  "audio_quality": true,
  "scene_review": true,
  "notes": "Any corrections made or remaining caveats"
}
```

Only attest to checks you actually performed. If corrections are needed, fix the source files and rerun. QC checks the source/license fields and logo transparency; it cannot establish that an attestation is true.

## Outputs

On pass, `production/` contains:

```text
newsVideo.mp4
subtitles.srt
newsThumbnail1.png
newsThumbnail2.png
newsThumbnail3.png
uploadInfo.txt
sourceRecord.txt
productionReport.json
transcript.txt
```

`productionReport.json` includes individual checks and render metadata. The current renderer creates broadcast-style static image/cards with hard cuts, burns captions into the video, and also supplies an SRT sidecar. It currently has no automatic B-roll search, narration-aware motion, music bed, lower-third entity verification, transitions, map/data visualization, or loudness normalization. The report/manual gate calls these editorial checks out instead of pretending they passed.

## Project map

- `midnet_news/` — executable CLI, orchestration, parsing, visual inventory, graphic compositor, FFmpeg render, and QC.
- `skills/` — input/process/output/validation/failure contracts for the specialist skills.
- `config/` — render, brand, subtitle, thumbnail and QC defaults.
- `brand/` — user-owned logo/font/theme assets (no fabricated logo or unlicensed font files).
- `input/` — runtime input convention and examples only.
- `workspace/` — generated intermediate work; do not publish.
- `production/` — final deliverables only after gate; QC report/source log also retained when held.

## Development

```bash
python -m pip install -e '.[test]'
pytest
```

See `SKILL.md` for agent instructions and `docs/` for contracts, safety boundaries, and the production checklist.
