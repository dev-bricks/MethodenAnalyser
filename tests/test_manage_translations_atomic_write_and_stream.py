"""
test_manage_translations_atomic_write_and_stream.py
Tests for atomic file writing, temporary file cleanup, and stream resilience in manage_translations.py.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import manage_translations as mt


def test_save_translations_atomic_write_creates_valid_json(tmp_path):
    """Verify save_translations writes valid UTF-8 JSON and leaves no temporary files."""
    trans_file = str(tmp_path / "locales" / "translations.json")
    data = {
        "hello": {"de": "Hallo", "en": "Hello", "es": "Hola", "zh": "你好", "ja": "こんにちは", "ru": "Привет"}
    }
    success = mt.save_translations(trans_file, data)
    assert success is True
    assert os.path.exists(trans_file)

    # Verify no .tmp files left in directory
    locales_dir = os.path.dirname(trans_file)
    tmp_files = [f for f in os.listdir(locales_dir) if ".tmp." in f]
    assert len(tmp_files) == 0

    # Verify content
    with open(trans_file, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded == data


def test_save_translations_preserves_original_on_failure(tmp_path):
    """Verify save_translations preserves existing file and cleans tempfile on dump failure."""
    trans_file = str(tmp_path / "translations.json")
    original_data = {"test": {"de": "Alt", "en": "Old"}}
    with open(trans_file, "w", encoding="utf-8") as f:
        json.dump(original_data, f)

    # Class with un-serializable object
    bad_data = {"test": {"de": object()}}

    success = mt.save_translations(trans_file, bad_data)
    assert success is False

    # Original file must be unchanged
    with open(trans_file, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded == original_data

    # No leftover .tmp files
    tmp_files = [f for f in os.listdir(str(tmp_path)) if ".tmp." in f]
    assert len(tmp_files) == 0


def test_manage_translations_cli_stats_subprocess():
    """Verify manage_translations.py --stats runs cleanly via CLI subprocess without encoding errors."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "manage_translations.py"), "--stats"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout is not None
    assert "DE:" in result.stdout
    assert "EN:" in result.stdout
    assert "ES:" in result.stdout
    assert "ZH:" in result.stdout
    assert "JA:" in result.stdout
    assert "RU:" in result.stdout


def test_manage_translations_cli_check_with_dir_argument(tmp_path):
    """Verify manage_translations.py --dir <dir> --check detects complete translations."""
    locales_dir = tmp_path / "locales"
    locales_dir.mkdir(parents=True)
    trans_file = locales_dir / "translations.json"
    data = {
        "greet": {"de": "Hallo", "en": "Hello", "es": "Hola", "zh": "你好", "ja": "こんにちは", "ru": "Привет"}
    }
    trans_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(ROOT / "manage_translations.py"), "--dir", str(tmp_path), "--check"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout is not None
    assert "100% Parit" in result.stdout or "100% Parität" in result.stdout
