# Final Packager Contract

**Purpose:** create a complete and traceable output package only after QC returns PASS.

- **Inputs:** QC-passed video/SRT/three thumbnails, three titles, 800–1000 character description, source record and render report.
- **Process:** verify file completeness and names; copy (not recompress) approved media; format upload metadata and retain provenance/report; never drop attribution or source notes.
- **Outputs:** `production/newsVideo.mp4`, `subtitles.srt`, `newsThumbnail1.png`–`3.png`, `uploadInfo.txt`, `sourceRecord.txt`, `productionReport.json`.
- **Validation:** all files present/non-empty; exact thumbnail sizes; report status PASS; metadata and sources present; hashes recorded in a future iteration.
- **Failure:** missing file, failed QC or missing approval → keep drafts in workspace; do not produce a misleading final package.

**v0.1 status:** orchestrator promotes media only after the technical and human gate passes; file hashes and archival bundles are not yet implemented.