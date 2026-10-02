# -*- coding: utf-8 -*-
"""Test suite for application icon assets, store logos and PWA manifests."""

import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def test_master_icon_properties():
    """Verify master icon format, size, and channels."""
    icon_png = ROOT / "MethodenAnalyser.png"
    assert icon_png.exists(), f"Master PNG missing: {icon_png}"
    with Image.open(icon_png) as img:
        assert img.format == "PNG"
        assert img.size in ((256, 256), (512, 512))
        assert img.mode in ("RGBA", "RGB")

    icon_ico = ROOT / "MethodenAnalyser.ico"
    assert icon_ico.exists(), f"Master ICO missing: {icon_ico}"
    with Image.open(icon_ico) as img:
        assert img.format == "ICO"


def test_store_tile_logos():
    """Verify Microsoft Store / MSIX tile logos have valid dimensions."""
    expected_tiles = {
        ROOT / "store_assets" / "Square44x44Logo.png": (44, 44),
        ROOT / "store_assets" / "Square150x150Logo.png": (150, 150),
        ROOT / "store_assets" / "Square310x310Logo.png": (310, 310),
        ROOT / "store_assets" / "Wide310x150Logo.png": (310, 150),
    }
    for file_path, size in expected_tiles.items():
        assert file_path.exists(), f"Tile icon missing: {file_path}"
        with Image.open(file_path) as img:
            assert img.size == size, f"Incorrect dimensions for {file_path}: {img.size} != {size}"
            assert img.format == "PNG"


def test_mobile_icons_suite():
    """Verify mobile_icons suite format and required resolutions."""
    mob_dir = ROOT / "mobile_icons"
    assert mob_dir.is_dir(), "mobile_icons directory must exist"

    manifest_file = mob_dir / "manifest.json"
    assert manifest_file.exists(), "mobile manifest.json must exist"
    data = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert "name" in data
    assert "icons" in data

    expected_sizes = {
        mob_dir / "icon-192.png": (192, 192),
        mob_dir / "icon-512.png": (512, 512),
        mob_dir / "apple-touch-icon-180.png": (180, 180),
    }
    for file_path, size in expected_sizes.items():
        assert file_path.exists(), f"Mobile icon missing: {file_path}"
        with Image.open(file_path) as img:
            assert img.size == size


def test_webapp_pwa_assets():
    """Verify webapp static and root icons and webmanifest."""
    static_manifest = ROOT / "webapp" / "static" / "manifest.webmanifest"
    assert static_manifest.exists(), "Static manifest.webmanifest must exist"
    manifest_data = json.loads(static_manifest.read_text(encoding="utf-8"))
    assert manifest_data.get("display") == "standalone"

    webapp_manifest = ROOT / "webapp" / "manifest.json"
    assert webapp_manifest.exists(), "Webapp manifest.json must exist"

    fav_ico = ROOT / "webapp" / "favicon.ico"
    assert fav_ico.exists(), "webapp favicon.ico must exist"


def test_banner_asset():
    """Verify README banner image exists and is valid."""
    banner_path = ROOT / "assets" / "banner.png"
    assert banner_path.exists(), "Banner image must exist"
    with Image.open(banner_path) as img:
        assert img.format == "PNG"
        assert img.width > 800
