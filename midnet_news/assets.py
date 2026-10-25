from __future__ import annotations

import json
from pathlib import Path

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm"}


def inventory_assets(src_dir: Path, workspace: Path, input_dir: Path) -> tuple[list[dict], list[dict]]:
    assets = []
    for path in sorted(src_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS | VIDEO_EXTENSIONS:
            assets.append({"asset_id": f"asset-{len(assets)+1:03d}", "filename": path.name,
                           "path": str(path.resolve()), "media_type": "image" if path.suffix.lower() in IMAGE_EXTENSIONS else "video",
                           "origin": "user-provided input/src", "license": "not independently verified; user-provided",
                           "editorial_status": "unreviewed", "use_in_video": False})
    review_file = input_dir / "asset-review.json"
    if review_file.exists():
        try:
            review = json.loads(review_file.read_text(encoding="utf-8"))
            by_path = {Path(item["path"]).name: item for item in review.get("assets", [])}
            for asset in assets:
                item = by_path.get(asset["filename"], {})
                if item.get("approved") is True:
                    asset["editorial_status"] = "approved by user"
                    asset["use_in_video"] = asset["media_type"] == "image"
                    asset["source_url"] = item.get("source_url", "")
                    asset["license"] = item.get("license", "user-attested; verify license details")
                    asset["notes"] = item.get("notes", "")
        except (ValueError, TypeError, KeyError) as exc:
            raise ValueError(f"Invalid {review_file}: {exc}") from exc
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "asset-manifest.json").write_text(json.dumps({"assets": assets}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return assets, [a for a in assets if a["use_in_video"]]


def write_source_record(assets: list[dict], path: Path) -> None:
    lines = ["MIDNET NEWS — VISUAL SOURCE RECORD", "", "Asset sourcing is not automated. Verify the original source, license, identity, event/date and editorial context before publication.", ""]
    if not assets:
        lines.append("No visual assets were supplied.")
    for asset in assets:
        lines += [f"[{asset['asset_id']}] {asset['filename']}", f"  File: {asset['path']}",
                  f"  Origin: {asset['origin']}", f"  Status: {asset['editorial_status']}",
                  f"  Source URL: {asset.get('source_url') or 'NOT PROVIDED'}", f"  License: {asset.get('license', 'unknown')}",
                  f"  Notes: {asset.get('notes', '')}", ""]
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
