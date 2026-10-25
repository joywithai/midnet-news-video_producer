from pathlib import Path

from PIL import Image, ImageChops

from midnet_news.design import make_thumbnail


def test_three_thumbnail_layouts_are_distinct(tmp_path: Path):
    titles = ["A major city development", "Officials release new findings", "What the report means"]
    files = []
    for i in range(3):
        path = tmp_path / f"thumb-{i}.png"
        make_thumbnail(path, titles[i], f"Concept {i+1}: key details", i, None, None)
        files.append(path)
        assert Image.open(path).size == (1280, 720)
    images = [Image.open(p).convert("RGB") for p in files]
    assert ImageChops.difference(images[0], images[1]).getbbox() is not None
    assert ImageChops.difference(images[1], images[2]).getbbox() is not None
