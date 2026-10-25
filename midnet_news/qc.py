from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageChops

from .subtitles import parse_srt

REVIEW_FIELDS = ("subtitle_sync", "visual_accuracy", "thumbnail_accuracy", "copyright_review", "audio_quality", "scene_review")


def run_qc(workspace: Path, production: Path, audio: Path, srt: Path, assets: list[dict], logo: Path,
           config: dict, render_info: dict | None, approval: dict | None = None) -> dict:
    checks = []
    approval = approval or {}
    def add(name, passed, detail, severity="blocker"):
        checks.append({"check": name, "passed": bool(passed), "severity": severity, "detail": detail})

    video = workspace / "draftVideo.mp4"
    add("video_present", video.is_file() and video.stat().st_size > 1024, str(video), "blocker")
    add("subtitle_syntax", _valid_srt(srt), "SRT cues parse and have positive durations", "blocker")
    thumbs = [workspace / f"draftThumbnail{i}.png" for i in range(1, 4)]
    add("three_thumbnails", all(p.is_file() for p in thumbs), "Three distinct draft PNGs exist", "blocker")
    sizes_ok = True
    for p in thumbs:
        try:
            with Image.open(p) as im:
                sizes_ok &= im.size == (config["thumbnails"]["width"], config["thumbnails"]["height"])
        except (OSError, FileNotFoundError):
            sizes_ok = False
    add("thumbnail_dimensions", sizes_ok, f"Expected {config['thumbnails']['width']}x{config['thumbnails']['height']}", "blocker")
    distinct = False
    if sizes_ok:
        try:
            imgs = [Image.open(p).convert("RGB") for p in thumbs]
            distinct = all(ImageChops.difference(imgs[a], imgs[b]).getbbox() is not None for a, b in ((0, 1), (0, 2), (1, 2)))
        except OSError:
            distinct = False
    add("thumbnail_distinctness", distinct, "Draft concepts differ across all three generated compositions", "blocker")
    add("logo_transparency", _has_transparency(logo), "Transparent PNG required; original source logo is not edited", "blocker")
    add("approved_visuals", any(a.get("use_in_video") for a in assets), "At least one visual is explicitly approved in input/asset-review.json", "blocker")
    missing_sources = [a["filename"] for a in assets if a.get("use_in_video") and (not a.get("source_url") or not a.get("license"))]
    add("visual_source_and_license", not missing_sources, "Missing source URL/license: " + (", ".join(missing_sources) if missing_sources else "none"), "blocker")
    add("source_record", (production / "sourceRecord.txt").is_file(), "Human-readable source record present", "blocker")
    if video.is_file() and shutil.which("ffprobe") and shutil.which("ffmpeg"):
        try:
            probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate,codec_name", "-of", "json", str(video)], capture_output=True, text=True, check=True)
            streams = json.loads(probe.stdout).get("streams", [])
            v = next(s for s in streams if s.get("codec_type") == "video")
            a = next(s for s in streams if s.get("codec_type") == "audio")
            dim_ok = (v.get("width"), v.get("height")) == (config["video"]["width"], config["video"]["height"])
            add("video_resolution", dim_ok, f"Detected {v.get('width')}x{v.get('height')}; expected configured resolution", "blocker")
            add("audio_video_streams", bool(v and a), "Video and audio streams present", "blocker")
            add("video_frame_rate", v.get("r_frame_rate") == f"{config['video']['fps']}/1", f"Detected {v.get('r_frame_rate')}; configured {config['video']['fps']}/1", "warning")
            decode = subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-f", "null", "-"], capture_output=True, text=True)
            add("full_decode", decode.returncode == 0, (decode.stderr[-1000:] or "Full FFmpeg decode passed").strip(), "blocker")
        except Exception as exc:
            add("media_probe", False, str(exc), "blocker")
    else:
        add("media_probe", False, "ffprobe/ffmpeg unavailable or draft video missing", "blocker")
    human_ok = approval.get("approved") is True and bool(str(approval.get("reviewer", "")).strip()) and all(approval.get(field) is True for field in REVIEW_FIELDS)
    add("human_editorial_approval", human_ok,
        "Reviewer must explicitly attest subtitle sync, visual/event accuracy, thumbnail accuracy, rights, audio and scene review in input/qc-approval.json.", "review")
    blockers_pass = all(c["passed"] for c in checks if c["severity"] == "blocker")
    review_pass = all(c["passed"] for c in checks if c["severity"] == "review")
    passed = blockers_pass and review_pass
    return {"status": "PASS" if passed else "NEEDS_REVIEW", "checks": checks,
            "render": render_info or {},
            "note": "Automated media checks do not establish factual accuracy or copyright clearance. Final delivery is gated on explicit human review."}


def _valid_srt(path: Path) -> bool:
    try:
        return bool(parse_srt(path))
    except (OSError, ValueError):
        return False


def _has_transparency(path: Path) -> bool:
    try:
        with Image.open(path) as image:
            if image.mode not in ("RGBA", "LA", "P"):
                return False
            alpha = image.getchannel("A") if image.mode in ("RGBA", "LA") else image.convert("RGBA").getchannel("A")
            return alpha.getextrema()[0] < 255
    except (OSError, FileNotFoundError):
        return False
