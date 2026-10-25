from pathlib import Path

from PIL import Image


def test_supplied_logo_is_hd_png_with_transparent_background():
    path = Path(__file__).resolve().parents[1] / "brand/logo/midnet-news-logo-hd.png"
    assert path.is_file()
    with Image.open(path) as image:
        assert image.format == "PNG"
        assert image.size == (1200, 1200)
        assert image.mode == "RGBA"
        alpha = image.getchannel("A")
        assert alpha.getextrema()[0] == 0
        assert alpha.getextrema()[1] == 255
        assert alpha.getpixel((0, 0)) == 0
