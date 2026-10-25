from __future__ import annotations

import re
from pathlib import Path


def parse_brief(path: Path) -> dict:
    """Parse a forgiving Markdown brief; headings and labeled lines are supported."""
    text = path.read_text(encoding="utf-8-sig")
    sections: dict[str, list[str]] = {}
    current = "_preamble"
    sections[current] = []
    for raw in text.splitlines():
        match = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", raw)
        if match:
            current = _key(match.group(1))
            sections.setdefault(current, [])
        else:
            sections.setdefault(current, []).append(raw)
    normalized = {key: "\n".join(lines).strip() for key, lines in sections.items()}

    def first(*keys: str) -> str:
        for key in keys:
            value = normalized.get(_key(key), "")
            if value:
                return value
        return ""

    titles_text = first("Titles", "Title Ideas", "YouTube Titles")
    titles = _extract_list(titles_text)[:3]
    ideas_text = first("Thumbnail Ideas", "Thumbnail Concepts", "Thumbnail")
    ideas = _extract_list(ideas_text)[:3]
    resource_text = first("Photo / Resource Names", "Photo Resource Names", "Resources", "Visuals")
    resources = _extract_list(resource_text)
    full_news = first("Full News", "English Full News", "News Script", "Script")
    # If a brief has a combined bilingual section but no recognized English heading,
    # fail validation rather than silently treating arbitrary text as a script.
    description = first("Description", "YouTube Description")
    return {
        "raw": text,
        "sections": normalized,
        "full_news": full_news,
        "titles": titles,
        "thumbnail_ideas": ideas,
        "resources": resources,
        "description": _strip_label(description),
    }


def _key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _extract_list(value: str) -> list[str]:
    result = []
    for line in value.splitlines():
        line = re.sub(r"^\s*(?:[-*+]\s+|\d+[.)]\s+|\[[ xX]\]\s*)", "", line).strip()
        if line and not line.startswith("<!--"):
            result.append(line)
    return result


def _strip_label(value: str) -> str:
    return re.sub(r"^\s*(?:description\s*:\s*)", "", value, flags=re.I).strip()
