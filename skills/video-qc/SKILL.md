# News Video QC Contract

**Purpose:** final technical and editorial gate; never infer factual correctness from a successful render.

- **Inputs:** draft video, subtitles and audio, brief, visual/source records, three thumbnails, upload metadata.
- **Technical checks:** full media decode; resolution/fps/codecs/streams/duration; black/frozen frames; missing media; audio level/clipping; subtitle syntax/timing/reading speed; thumbnail size/mobile preview; output completeness.
- **Editorial checks:** audio-caption sync and words; person/place/event accuracy; archive labels; no stretching, misleading image/graphic or repeated image; thumbnail-video-title consistency; source/license/attribution completeness; logo/title/subtitle safe areas.
- **Outputs:** `productionReport.json` with each check, evidence and disposition. `PASS` only after blockers and explicitly named editor's required attestations pass.
- **Failure:** return a specific actionable issue to the responsible skill; v0.1 has no automatic retries. Set `NEEDS_REVIEW`; do not create final-named media. A future retry implementation may allow at most two retries per stage.

**v0.1 status:** automated SRT syntax, thumbnail dimensions, transparent logo presence, user-approved asset/source fields, FFprobe stream/resolution and full decode; an explicit human approval file gates release. Detailed synchronization, audio loudness, black/frozen frame and editorial accuracy tests remain manual.