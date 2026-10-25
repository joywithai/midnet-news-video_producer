from pathlib import Path

from midnet_news.orchestrator import produce


def test_orchestrator_fails_closed_without_render_or_human_review(tmp_path: Path):
    repo = Path(__file__).resolve().parents[1]
    inp = tmp_path / "input"
    inp.mkdir()
    (inp / "audio.wav").write_bytes(b"not-real-audio")
    (inp / "subtitles.srt").write_text("1\n00:00:00,000 --> 00:00:01,000\nA test caption.\n", encoding="utf-8")
    description = "Verified description. " + ("Context and background for this report. " * 24)
    (inp / "brief.md").write_text(
        "# English Full News\nThis is a sufficiently long and clearly labeled English news script for a project test. "
        "It is only a test and includes enough context to satisfy the workflow input contract.\n"
        "# Photo / Resource Names\n- Verified source image needed\n"
        "# Thumbnail Ideas\n1. City view headline\n2. Document detail\n3. Map concept\n"
        "# Titles\n1. First accurate title\n2. Second accurate title\n3. Third accurate title\n"
        f"# Description\n{description}\n", encoding="utf-8")
    out = tmp_path / "production"
    report = produce(inp, out, repo, repo / "config/production.json")
    assert report["status"] == "NEEDS_REVIEW"
    assert (repo / "workspace/drafts/draftThumbnail1.png").is_file()
    assert not (out / "newsVideo.mp4").exists()
    assert (out / "productionReport.json").is_file()
