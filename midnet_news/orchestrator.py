from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from .assets import inventory_assets, write_source_record
from .brief import parse_brief
from .design import make_thumbnail
from .qc import run_qc
from .render import render_video
from .subtitles import ensure_subtitles, parse_srt


def _write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _select_audio(input_dir: Path) -> Path:
    files = sorted(p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in {".mp3", ".wav"})
    if len(files) != 1:
        raise ValueError(f"Expected exactly one audio.mp3 or audio.wav in {input_dir}; found {len(files)}.")
    return files[0]


def _validate_brief(brief: dict):
    problems = []
    if len(brief["full_news"]) < 80:
        problems.append("brief.md must contain a substantial English Full News section.")
    if len(brief["titles"]) != 3:
        problems.append(f"brief.md needs exactly 3 titles; found {len(brief['titles'])}.")
    if len(brief["thumbnail_ideas"]) != 3:
        problems.append(f"brief.md needs exactly 3 thumbnail ideas; found {len(brief['thumbnail_ideas'])}.")
    if not brief["resources"]:
        problems.append("brief.md needs Photo / Resource Names (at least one line; use 'none' only when editor confirms no visual is needed).")
    if not brief["description"]:
        problems.append("brief.md needs a Description section.")
    if problems:
        raise ValueError("Input validation failed:\n- " + "\n- ".join(problems))


def produce(input_dir: Path, output_dir: Path, repo_dir: Path, config_path: Path, asr_model: str = "small") -> dict:
    input_dir, output_dir, repo_dir = input_dir.resolve(), output_dir.resolve(), repo_dir.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    brief_path = input_dir / "brief.md"
    if not brief_path.is_file():
        raise ValueError(f"Missing required input file: {brief_path}")
    brief = parse_brief(brief_path)
    _validate_brief(brief)
    audio = _select_audio(input_dir)
    workspace = repo_dir / "workspace"
    drafts = workspace / "drafts"
    drafts.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    assets, approved = inventory_assets(input_dir / "src", workspace, input_dir)
    write_source_record(assets, output_dir / "sourceRecord.txt")
    srt_in = input_dir / "subtitles.srt"
    srt, transcript, timing = ensure_subtitles(audio, srt_in if srt_in.exists() else None,
                                                brief["full_news"], workspace / "subtitles", model=asr_model)
    draft_srt = drafts / "subtitles.srt"
    shutil.copy2(srt, draft_srt)
    shutil.copy2(transcript, drafts / "transcript.txt")
    shutil.copy2(timing, drafts / "timing.json")

    configured_logo = repo_dir / config["brand"]["logo_path"]
    external_logo = input_dir / "brand" / "logo" / "midnet-news-logo-hd.png"
    logo = configured_logo if configured_logo.exists() else external_logo
    logo_for_render = logo if logo.exists() else None
    visuals = [Path(a["path"]) for a in approved if a["media_type"] == "image"]
    for idx in range(3):
        make_thumbnail(drafts / f"draftThumbnail{idx+1}.png", brief["titles"][idx], brief["thumbnail_ideas"][idx], idx,
                       visuals[idx % len(visuals)] if visuals else None, logo_for_render)
    upload_info = _write_upload_info(brief, drafts / "uploadInfo.txt")

    cues = parse_srt(draft_srt)
    render_info = None
    try:
        render_info = render_video(audio, draft_srt, cues, brief["full_news"], brief["titles"][0],
                                   approved, logo_for_render, workspace / "render", drafts / "draftVideo.mp4", config)
    except (RuntimeError, OSError) as exc:
        (workspace / "render-error.txt").write_text(str(exc) + "\n", encoding="utf-8")

    approval = {}
    approval_path = input_dir / "qc-approval.json"
    if approval_path.exists():
        approval = json.loads(approval_path.read_text(encoding="utf-8"))
    report = run_qc(drafts, output_dir, audio, draft_srt, assets, logo, config, render_info, approval)
    report.update({"created_utc": datetime.now(timezone.utc).isoformat(), "input_audio": audio.name,
                   "brief": str(brief_path), "description_characters": len(brief["description"]),
                   "description_length_in_range": 800 <= len(brief["description"]) <= 1000,
                   "pipeline": "local-first v0.1; no remote asset downloading or unlicensed third-party services"})
    if not report["description_length_in_range"]:
        report["checks"].append({"check": "description_length", "passed": False, "severity": "review",
                                 "detail": f"Description is {len(brief['description'])} characters; target is 800–1000."})
        report["status"] = "NEEDS_REVIEW"
    if report["status"] == "PASS":
        shutil.copy2(drafts / "draftVideo.mp4", output_dir / "newsVideo.mp4")
        shutil.copy2(draft_srt, output_dir / "subtitles.srt")
        for idx in range(1, 4):
            shutil.copy2(drafts / f"draftThumbnail{idx}.png", output_dir / f"newsThumbnail{idx}.png")
        shutil.copy2(upload_info, output_dir / "uploadInfo.txt")
        shutil.copy2(drafts / "transcript.txt", output_dir / "transcript.txt")
    else:
        report["delivery_note"] = "Final-named video, subtitle and thumbnail files are withheld until technical QC and human editorial approval pass. Drafts remain under workspace/drafts/."
    _write_json(output_dir / "productionReport.json", report)
    _write_json(workspace / "input-manifest.json", {"audio": str(audio), "brief": str(brief_path), "assets": assets,
                                                      "srt": str(draft_srt), "timing": str(timing)})
    return report


def _write_upload_info(brief: dict, path: Path):
    lines = ["MIDNET NEWS — YOUTUBE UPLOAD INFO", "", "TITLES", ""]
    for i, title in enumerate(brief["titles"], 1):
        lines.append(f"Title {i}: {title}")
    lines += ["", "DESCRIPTION", "", brief["description"], ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
