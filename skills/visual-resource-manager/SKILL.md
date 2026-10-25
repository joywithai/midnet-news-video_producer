# News Visual Resource Manager Contract

**Purpose:** inventory supplied images/video, preserve provenance, and prevent unverified material from being treated as verified news footage.

- **Inputs:** `brief.md` Photo/Resource Names and `input/src/` files; optional `input/asset-review.json`.
- **Process:** inventory filename/type/path; capture source URL, license, attribution and context notes; check identity, place, event/date, duplicates, quality, archive status and relevance before approval. Never infer identity from filename alone. Separate generated/illustrative graphics from documentary imagery.
- **Outputs:** `workspace/asset-manifest.json`, `production/sourceRecord.txt`, eligible user-attested visuals.
- **Validation:** approval is explicit; user-provided files stay unreviewed by default. Missing source/license/context or duplicates are flagged. Editorial relevance and licensing are ultimately human determinations.
- **Failure:** missing/ambiguous/unlicensed asset → do not use, record the gap and request a verified asset. No misleading substitution.

**v0.1 status:** inventories local media and reads a user-authored review JSON; no remote asset search/download, perceptual duplicate check, identity check or independent license verification.