# Motion Graphics Skill Contract

**Purpose:** render a consistent 16:9 MidNet News draft from a reviewed scene plan.

- **Inputs:** audio, subtitles, approved mapped visual assets, scene timeline, original transparent logo, licensed fonts and brand configuration.
- **Process:** compose scenes with restrained camera motion, lower thirds/data cards only when sourced, transitions, caption-safe placement, logo in a consistent top corner, and clean audio. Preserve aspect ratios; no stretching. Apply consistent voice loudness and encode H.264/AAC.
- **Outputs:** `draftVideo.mp4`, `render-report.json`; never directly name an unchecked render as final.
- **Validation:** probe resolution/fps/codecs/duration; full decode; check all assets/fonts resolve; inspect frame sequence and audio.
- **Failure:** missing media/codec/font or render errors → retain diagnostic, stop final packaging, retry only within configured limit.

**v0.1 status:** FFmpeg renders static branded cards with hard cuts, burns captions and retains the original audio. It does not yet implement Remotion, camera movement, transitions, audio normalization, timeline-level visual association or motion templates.