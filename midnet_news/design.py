from __future__ import annotations

import re
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

NAVY = (7, 27, 54)
RED = (227, 38, 54)
WHITE = (255, 255, 255)


def _font(size: int, bold: bool = True):
    candidates = [
        Path("brand/fonts/headline/MidNetHeadline.ttf") if bold else Path("brand/fonts/body/MidNetBody.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/Library/Fonts/Arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            try:
                return ImageFont.truetype(str(candidate), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def _fit_text(draw, text, max_width, start_size, max_lines=3):
    words = text.split()
    for size in range(start_size, 19, -2):
        font = _font(size)
        lines, line = [], ""
        for word in words:
            trial = (line + " " + word).strip()
            if draw.textbbox((0, 0), trial, font=font)[2] <= max_width:
                line = trial
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
        if len(lines) <= max_lines:
            return font, lines
    return _font(20), textwrap.wrap(text, width=20)[:max_lines]


def _open_image(path: Path | None, size: tuple[int, int]) -> Image.Image:
    if path and path.exists():
        try:
            return ImageOps.fit(Image.open(path).convert("RGB"), size, method=Image.Resampling.LANCZOS)
        except OSError:
            pass
    im = Image.new("RGB", size, NAVY)
    d = ImageDraw.Draw(im)
    for x in range(0, size[0], 80):
        d.line((x, 0, x - size[1], size[1]), fill=(12, 40, 72), width=2)
    return im


def _paste_logo(image: Image.Image, logo_path: Path | None, margin: int, width: int, corner="top-right"):
    if not logo_path or not logo_path.exists():
        return
    try:
        logo = Image.open(logo_path).convert("RGBA")
        h = max(1, round(logo.height * width / logo.width))
        logo.thumbnail((width, h), Image.Resampling.LANCZOS)
        x = image.width - margin - logo.width if corner == "top-right" else margin
        # Respect existing alpha; do not recolor or alter the source asset.
        image.paste(logo, (x, margin), logo)
    except OSError:
        return


def make_thumbnail(path: Path, title: str, idea: str, variant: int, source: Path | None, logo: Path | None):
    size = (1280, 720)
    image = _open_image(source, size)
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    if variant == 0:  # left editorial panel
        d.rectangle((0, 0, 650, 720), fill=(*NAVY, 238))
        d.rectangle((0, 0, 18, 720), fill=(*RED, 255))
        text_box = (64, 250, 570)
    elif variant == 1:  # lower broadcast strap
        d.rectangle((0, 430, 1280, 720), fill=(*NAVY, 235))
        d.rectangle((0, 430, 1280, 448), fill=(*RED, 255))
        text_box = (64, 485, 1140)
    else:  # diagonal corner treatment
        d.polygon([(0, 0), (800, 0), (590, 720), (0, 720)], fill=(*NAVY, 232))
        d.rectangle((0, 0, 16, 720), fill=(*RED, 255))
        text_box = (60, 235, 550)
    image = Image.alpha_composite(image.convert("RGBA"), overlay)
    d = ImageDraw.Draw(image)
    tag_font = _font(30)
    tag_y = text_box[1] - 72
    d.rounded_rectangle((text_box[0], tag_y, text_box[0] + 255, tag_y + 52), radius=8, fill=RED)
    d.text((text_box[0] + 16, tag_y + 8), "MIDNET NEWS", font=tag_font, fill=WHITE)
    # The concept may describe a visual, not copy. Use explicit "Text: ..." copy when
    # present; otherwise derive a short, non-fabricated phrase from the supplied title.
    explicit = re.search(r"\btext\s*:\s*([^;|]+)", idea or "", flags=re.I)
    chosen = explicit.group(1).strip() if explicit else " ".join(title.split()[:5])
    chosen = " ".join(chosen.split()[:5])
    font, lines = _fit_text(d, chosen.upper(), text_box[2], 64, max_lines=4)
    y = text_box[1]
    for line in lines:
        d.text((text_box[0], y), line, font=font, fill=WHITE, stroke_width=2, stroke_fill=(0, 0, 0, 130))
        y += font.size + 12
    _paste_logo(image, logo, 34, 150)
    image.convert("RGB").save(path, "PNG", optimize=True)


def make_scene_card(path: Path, text: str, headline: str, source: Path | None, logo: Path | None, config: dict):
    width, height = config["video"]["width"], config["video"]["height"]
    image = _open_image(source, (width, height)).convert("RGBA")
    shade = Image.new("RGBA", image.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(shade)
    d.rectangle((0, 0, width, 165), fill=(*NAVY, 230))
    d.rectangle((0, height - 310, width, height), fill=(*NAVY, 223))
    d.rectangle((0, height - 310, 18, height), fill=(*RED, 255))
    image = Image.alpha_composite(image, shade)
    d = ImageDraw.Draw(image)
    d.rounded_rectangle((64, 52, 330, 112), radius=8, fill=RED)
    d.text((83, 62), "MIDNET NEWS", font=_font(32), fill=WHITE)
    headline = headline.strip() or "LATEST NEWS"
    hf, hl = _fit_text(d, headline.upper(), width - 160, 56, 2)
    for i, line in enumerate(hl[:2]):
        d.text((64, 185 + i * (hf.size + 12)), line, font=hf, fill=WHITE)
    body = text.strip()
    if body:
        sf, sl = _fit_text(d, body, width - 160, config["subtitles"]["font_size"], 2)
        for i, line in enumerate(sl[:2]):
            box = d.textbbox((0, 0), line, font=sf)
            x = (width - (box[2] - box[0])) // 2
            y = height - 160 + i * (sf.size + 10)
            d.text((x + 3, y + 3), line, font=sf, fill=(0, 0, 0, 255), stroke_width=3, stroke_fill=(0, 0, 0, 180))
            d.text((x, y), line, font=sf, fill=WHITE)
    _paste_logo(image, logo, config["brand"]["safe_margin"], config["brand"]["logo_width"], config["brand"]["logo_position"])
    image.convert("RGB").save(path, "PNG", optimize=True)
