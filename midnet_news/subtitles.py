from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path


def parse_srt(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8-sig")
    blocks = re.split(r"\n\s*\n", text.strip()) if text.strip() else []
    cues = []
    for block in blocks:
        lines = block.splitlines()
        time_line = next((line for line in lines if "-->" in line), None)
        if not time_line:
            continue
        left, right = [part.strip().split()[0] for part in time_line.split("-->", 1)]
        content = " ".join(line.strip() for line in lines[lines.index(time_line) + 1:]).strip()
        start, end = _srt_seconds(left), _srt_seconds(right)
        if end <= start or not content:
            raise ValueError(f"Invalid subtitle cue in {path}: {time_line}")
        cues.append({"start": start, "end": end, "text": content})
    if not cues:
        raise ValueError(f"No valid SRT cues found in {path}")
    for previous, current in zip(cues, cues[1:]):
        if current["start"] < previous["start"] or current["start"] < previous["end"]:
            raise ValueError(f"Subtitle cues are out of order or overlap in {path}")
    return cues


def _srt_seconds(value: str) -> float:
    h, m, rest = value.replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(rest)


def _srt_time(seconds: float) -> str:
    ms = max(0, round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def transcribe(audio: Path, script: str, out_dir: Path, model: str = "small", device: str = "cpu") -> tuple[Path, Path, Path]:
    """Transcribe with optional faster-whisper. No synthetic timings are invented."""
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError("No subtitles supplied. Install the optional ASR extra: pip install -e '.[asr]' (faster-whisper).") from exc
    model_obj = WhisperModel(model, device=device, compute_type="int8" if device == "cpu" else "float16")
    segments, info = model_obj.transcribe(str(audio), word_timestamps=True, vad_filter=True)
    cues = []
    transcript = []
    for seg in segments:
        text = (seg.text or "").strip()
        if text:
            cues.append({"start": float(seg.start), "end": float(seg.end), "text": text})
            transcript.append(text)
    if not cues:
        raise RuntimeError("ASR returned no speech segments.")
    out_dir.mkdir(parents=True, exist_ok=True)
    srt_path, txt_path, timing_path = out_dir / "subtitles.srt", out_dir / "transcript.txt", out_dir / "timing.json"
    write_srt(cues, srt_path)
    txt_path.write_text("\n".join(transcript) + "\n", encoding="utf-8")
    timing_path.write_text(json.dumps({"language": info.language, "language_probability": info.language_probability,
                                      "alignment": "whisper segment timestamps; English script provided as editorial reference, not substituted for heard words",
                                      "cues": cues}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return srt_path, txt_path, timing_path


def write_srt(cues: list[dict], path: Path) -> None:
    lines = []
    for i, cue in enumerate(cues, 1):
        lines += [str(i), f"{_srt_time(cue['start'])} --> {_srt_time(cue['end'])}", cue["text"], ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def ensure_subtitles(audio: Path, provided_srt: Path | None, script: str, out_dir: Path, model: str = "small"):
    if provided_srt:
        cues = parse_srt(provided_srt)
        out_dir.mkdir(parents=True, exist_ok=True)
        srt_path = out_dir / "subtitles.srt"
        shutil.copy2(provided_srt, srt_path)
        transcript_path = out_dir / "transcript.txt"
        transcript_path.write_text("\n".join(c["text"] for c in cues) + "\n", encoding="utf-8")
        timing_path = out_dir / "timing.json"
        timing_path.write_text(json.dumps({"source": "provided SRT", "cues": cues}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return srt_path, transcript_path, timing_path
    return transcribe(audio, script, out_dir, model=model)
