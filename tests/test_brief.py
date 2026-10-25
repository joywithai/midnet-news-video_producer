from pathlib import Path

from midnet_news.brief import parse_brief


def test_parse_brief_lists_and_script(tmp_path: Path):
    brief = tmp_path / "brief.md"
    brief.write_text("""# English Full News\nThis is a sufficiently detailed English script that describes the news and its context for a spoken report.\n\n# Titles\n1. First title\n2. Second title\n3. Third title\n\n# Thumbnail Ideas\n- First concept\n- Second concept\n- Third concept\n\n# Photo / Resource Names\n- City hall\n\n# Description\nA description here.\n""", encoding="utf-8")
    result = parse_brief(brief)
    assert "sufficiently detailed" in result["full_news"]
    assert result["titles"] == ["First title", "Second title", "Third title"]
    assert result["thumbnail_ideas"] == ["First concept", "Second concept", "Third concept"]
    assert result["resources"] == ["City hall"]
