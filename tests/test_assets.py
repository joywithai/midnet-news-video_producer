import json
from pathlib import Path

from midnet_news.assets import inventory_assets


def test_assets_default_unreviewed_and_user_approval(tmp_path: Path):
    src = tmp_path / "input/src"
    src.mkdir(parents=True)
    (src / "event.jpg").write_bytes(b"placeholder")
    workspace = tmp_path / "workspace"
    assets, approved = inventory_assets(src, workspace, tmp_path / "input")
    assert len(assets) == 1 and not approved
    (tmp_path / "input/asset-review.json").write_text(json.dumps({"assets": [{"path": "event.jpg", "approved": True, "source_url": "https://example.test/image", "license": "CC BY 4.0"}]}))
    assets, approved = inventory_assets(src, workspace, tmp_path / "input")
    assert len(approved) == 1
    assert assets[0]["editorial_status"] == "approved by user"
