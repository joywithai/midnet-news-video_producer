from pathlib import Path

import pytest

from midnet_news.subtitles import parse_srt, write_srt


def test_srt_round_trip(tmp_path: Path):
    path = tmp_path / "test.srt"
    write_srt([{"start": 0.0, "end": 1.25, "text": "Hello, newsroom."}], path)
    cue = parse_srt(path)[0]
    assert cue["start"] == 0
    assert cue["end"] == 1.25
    assert cue["text"] == "Hello, newsroom."


def test_reject_invalid_srt(tmp_path: Path):
    path = tmp_path / "bad.srt"
    path.write_text("1\n00:00:01,000 --> 00:00:00,000\nBad\n", encoding="utf-8")
    with pytest.raises(ValueError):
        parse_srt(path)
