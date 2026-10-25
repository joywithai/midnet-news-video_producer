# Audio-to-SRT Skill Contract

**Purpose:** produce timestamps from the supplied narration recording and a transcript that is auditable against the provided English Full News script.

- **Inputs:** exactly one MP3/WAV; optional `input/subtitles.srt`; `brief.md` English Full News.
- **Process:** validate/read audio; if SRT exists, parse and validate monotonic positive cue durations. Otherwise use explicitly installed local faster-whisper with word timestamps/VAD. Keep ASR words as heard. Use the brief for human review of names/terms; do not silently replace ASR text with script text. Segment cues for readable line lengths and safe reading speed in later versions.
- **Outputs:** `subtitles.srt`, `transcript.txt`, `timing.json` in workspace; SRT copied to final only after QC pass.
- **Validation:** parse all cues; check timestamps and ordering, duration, SRT formatting, transcript coverage. Human must compare timing/spelling against audio and script.
- **Failure:** missing optional ASR package/model/audio, empty speech, malformed SRT, or mismatch → fail stage/NEEDS_REVIEW; never fabricate timestamps. Install `.[asr]` or supply a corrected SRT.

**v0.1 status:** local Whisper segments retain timestamps; no script-forced alignment or automatic spelling correction is claimed. The reference script is not a substitute for heard audio.