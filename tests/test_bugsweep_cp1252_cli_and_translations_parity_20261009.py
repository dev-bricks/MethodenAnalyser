"""Tests for BS-02 cp1252 CLI resilience and Tier-2 manage_translations parity tooling."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import manage_translations as mt
import MethodenAnalyser3 as m3


def test_generate_report_name_matches_uses_ascii_arrow_and_cp1252_safe():
    """Verify generate_report formats name_matches with ASCII '->' and encodes in cp1252 cleanly."""
    res = m3.analyze_source("def calc_total():\n    pass\n\ncalc_totall()\n")
    assert len(res.name_matches) > 0

    report = m3.generate_report(res)

    # Must contain ASCII arrow ->
    assert "-> " in report
    # Must NOT contain unicode arrow \u2192
    assert "\u2192" not in report
    assert "calc_totall" in report
    assert "calc_total" in report

    # Must encode cleanly in Windows standard cp1252 encoding without error
    encoded = report.encode("cp1252", errors="strict")
    assert b"-> " in encoded
    assert b"calc_totall" in encoded


def test_emit_cli_report_handles_unicode_encode_error():
    """Verify _emit_cli_report catches UnicodeEncodeError and uses replacement rather than crashing."""
    class RestrictedWriter:
        def __init__(self, encoding="ascii"):
            self.encoding = encoding
            self.buffer = []

        def write(self, s: str) -> int:
            s.encode(self.encoding, errors="strict")
            self.buffer.append(s)
            return len(s)

        def getvalue(self) -> str:
            return "".join(self.buffer)

    mock_stdout = RestrictedWriter("ascii")
    with patch("sys.stdout", mock_stdout):
        # Pass non-ascii string
        m3._emit_cli_report("Test mit Umlauten: äöü und Symbolen: →")

    output = mock_stdout.getvalue()
    assert "Test mit Umlauten: " in output
    # Characters that couldn't be encoded in ASCII are replaced with ?
    assert "?" in output


def test_manage_translations_check_passes_on_repository():
    """Verify check_translations returns True on the repository's 6-language catalog."""
    assert mt.check_translations(str(ROOT)) is True


def test_manage_translations_check_detects_missing_language(tmp_path):
    """Verify check_translations returns False when a language is missing."""
    locales_dir = tmp_path / "locales"
    locales_dir.mkdir(parents=True)
    incomplete_catalog = {
        "btn_test": {
            "de": "Testen",
            "en": "Test",
            "es": "Probar",
            "zh": "测试",
            "ja": "テスト",
            # missing "ru"
        }
    }
    (locales_dir / "translations.json").write_text(json.dumps(incomplete_catalog), encoding="utf-8")
    assert mt.check_translations(str(tmp_path)) is False


def test_manage_translations_show_stats_executes_cleanly(capsys):
    """Verify show_stats executes and outputs coverage for all 6 languages."""
    mt.show_stats(str(ROOT))
    captured = capsys.readouterr()
    for lang in ["DE:", "EN:", "ES:", "ZH:", "JA:", "RU:"]:
        assert lang in captured.out
    assert "100.0%" in captured.out


def test_manage_translations_cli_check_exit_code():
    """Verify manage_translations.py --check exits with code 0."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "manage_translations.py"), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "100% Parit" in result.stdout or "100% Parität" in result.stdout


def test_cli_execution_with_name_matches_under_cp1252(tmp_path):
    """End-to-end CLI execution with near-match call and definition under cp1252."""
    code_file = tmp_path / "typo_call.py"
    code_file.write_text(
        "def compute_total(val):\n    return val * 2\n\ncompute_totall(10)\n",
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "cp1252"

    result = subprocess.run(
        [sys.executable, str(ROOT / "MethodenAnalyser3.py"), "--file", str(code_file)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="cp1252",
        errors="replace",
        env=env,
        check=False,
    )

    # Should not crash with UnicodeEncodeError
    assert "UnicodeEncodeError" not in result.stderr
    assert "compute_totall" in result.stdout
    assert "->" in result.stdout
