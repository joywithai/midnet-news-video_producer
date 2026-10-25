from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from .design import make_scene_card


def _run(command: list[str], cwd: Path | None = None):
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if result.returncode:
        detail = (result.stderr or result.stdout)[-4000:]
        raise RuntimeError(f"Command failed ({result.returncode}): {' '.join(command[:5])} ...\n{detail}")
    return result.stdout.strip()


def probe_duration(audio: Path) -> float:
    if not shutil.which("ffprobe"):
        raise RuntimeError("ffprobe is required. Install FFmpeg (ffmpeg and ffprobe must be on PATH).")
    raw = _run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(audio)])
    duration = float(json.loads(raw)["format"]["duration"])
    if duration <= 0:
        raise RuntimeError("Audio duration could not be determined.")
    return duration


def render_video(audio: Path, srt: Path, cues: list[dict], script: str, headline: str,
                 approved_visuals: list[dict], logo: Path | None, work_dir: Path, output: Path, config: dict) -> dict:
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("FFmpeg and FFprobe are required; install a recent FFmpeg build and retry.")
    duration = probe_duration(audio)
    scene_dir = work_dir / "scene-cards"
    scene_dir.mkdir(parents=True, exist_ok=True)
    interval = 6.0
    scene_count = int((duration + interval - 0.001) // interval) + 1
    scene_count = min(scene_count, 1000)
    cue_index = 0
    scene_files = []
    for idx in range(scene_count):
        start = idx * interval
        end = min(duration, start + interval)
        if start >= duration:
            break
        midpoint = (start + end) / 2
        while cue_index + 1 < len(cues) and cues[cue_index]["end"] < midpoint:
            cue_index += 1
        cue = cues[cue_index] if cues and cues[cue_index]["start"] <= midpoint <= cues[cue_index]["end"] else {}
        body = cue.get("text", "")
        visual = None
        if approved_visuals:
            # Only user-attested assets are eligible. Round-robin is explicit in the manifest;
            # editorial relevance still requires a human review before release.
            visual = Path(approved_visuals[idx % len(approved_visuals)]["path"])
        image = scene_dir / f"scene-{idx:04d}.png"
        make_scene_card(image, body, headline, visual, logo, config)
        scene_files.append((image.name, end - start))
    if not scene_files:
        raise RuntimeError("No scene cards were created.")
    concat = scene_dir / "scenes.txt"
    lines = []
    for name, seconds in scene_files:
        lines.append(f"file '{name}'")
        lines.append(f"duration {seconds:.3f}")
    # concat demuxer uses the following file to honor the last duration.
    lines.append(f"file '{scene_files[-1][0]}'")
    concat.write_text("\n".join(lines) + "\n", encoding="utf-8")
    work_dir.mkdir(parents=True, exist_ok=True)
    srt_copy = scene_dir / "subtitles.srt"
    shutil.copy2(srt, srt_copy)
    # Relative filter path avoids platform-specific drive/path escaping.
    subtitles_filter = "subtitles=filename=subtitles.srt:force_style='FontName=DejaVu Sans,FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1,MarginV=70,Alignment=2'"
    output.parent.mkdir(parents=True, exist_ok=True)
    command = ["ffmpeg", "-hide_banner", "-y", "-f", "concat", "-safe", "0", "-i", "scenes.txt",
               "-i", str(audio.resolve()), "-t", f"{duration:.3f}", "-vf", subtitles_filter,
               "-map", "0:v:0", "-map", "1:a:0", "-r", str(config["video"]["fps"]),
               "-c:v", "libx264", "-preset", config["video"]["preset"], "-crf", str(config["video"]["crf"]),
               "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", config["video"]["audio_bitrate"],
               "-movflags", "+faststart", str(output.resolve())]
    _run(command, cwd=scene_dir)
    return {"duration_seconds": round(duration, 3), "scene_count": len(scene_files), "resolution": f"{config['video']['width']}x{config['video']['height']}",
            "fps": config["video"]["fps"], "video_codec": "H.264", "audio_codec": "AAC", "render_mode": "static broadcast cards with hard cuts; captions burned in and supplied separately"}
