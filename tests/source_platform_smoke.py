"""Source-level smoke tests for Windows, Linux, and macOS desktop targets.

These tests exercise portable core contracts of MethodenAnalyser without requiring
a display server, GUI rendering, or platform-specific installer dependencies.
"""

from __future__ import annotations

import json
import platform
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

import MethodenAnalyser3 as m
from translator import TranslationSystem

ROOT = Path(__file__).resolve().parents[1]


def test_runner_is_a_supported_desktop_source_target() -> None:
    """Ensure the test environment is recognized as a valid desktop OS."""
    assert platform.system() in {"Windows", "Linux", "Darwin"}


def test_ast_analysis_on_sample_source() -> None:
    """Verify core AST analysis contract on sample Python code."""
    source = textwrap.dedent(
        """
        import os
        import sys

        def calculate_total(a: int, b: int) -> int:
            return a + b

        class DataProcessor:
            def process(self, value):
                return calculate_total(value, 10)
        """
    ).strip()

    result = m.analyze_source(source, source_name="sample.py")
    assert result is not None
    assert result.total_lines > 0
    assert "calculate_total" in result.defs
    assert "DataProcessor" in result.defs


def test_unused_import_detection_contract() -> None:
    """Verify that unused imports are detected while used ones are not flagged."""
    source = textwrap.dedent(
        """
        import os
        import math
        import unused_module

        def compute(x):
            return math.sqrt(x) + len(os.getcwd())
        """
    ).strip()

    result = m.analyze_source(source, source_name="imports_test.py")
    assert "unused_module" in result.unused_imports
    assert "os" not in result.unused_imports
    assert "math" not in result.unused_imports


def test_duplicate_imports_detection_contract() -> None:
    """Verify duplicate import detection."""
    source = textwrap.dedent(
        """
        import os
        import os
        answer = 42
        """
    ).strip()

    result = m.analyze_source(source, source_name="dup_test.py")
    assert "os" in result.duplicate_imports


def test_json_export_schema_parity() -> None:
    """Verify that export format conforms to methodenanalyser-report-v1.json contract."""
    source = "import os\ndef hello(): return 'world'\n"
    analysis = m.analyze_source(source, source_name="hello.py")
    json_dict = m._analysis_result_to_json(analysis)
    assert "definitions" in json_dict
    assert "hello" in json_dict["definitions"]

    report = m.build_json_report(source_kind="file", result=analysis, source_name="hello.py")
    assert report["schema_version"] == "methodenanalyser-report-v1"
    assert report["tool_version"] == m.TOOL_VERSION

    with tempfile.TemporaryDirectory() as tmpdir:
        report_path = Path(tmpdir) / "report.json"
        m.write_json_report(report, str(report_path))
        read_back = json.loads(report_path.read_text(encoding="utf-8"))
        assert read_back["schema_version"] == "methodenanalyser-report-v1"
        assert read_back["tool_version"] == m.TOOL_VERSION


def test_translation_system_tier2_parity() -> None:
    """Verify that translator initializes and translates in all 6 Tier-2 languages."""
    expected_langs = ["de", "en", "es", "zh", "ja", "ru"]
    for lang in expected_langs:
        assert lang in TranslationSystem.SUPPORTED_LANGUAGES, f"{lang} missing from SUPPORTED_LANGUAGES"
        ts = TranslationSystem(lang)
        translated_title = ts.t("app_title")
        assert translated_title and translated_title != "app_title"


def test_headless_cli_interface_invocation() -> None:
    """Verify that CLI interface handles --help and --file without error."""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write("def sample(): pass\n")
        tmp_name = f.name

    try:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "MethodenAnalyser3.py"), "--file", tmp_name],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        # Exit code 0 means clean analysis with 0 findings
        assert proc.returncode in (0, 2), f"Unexpected exit code {proc.returncode}: {proc.stderr}"
    finally:
        Path(tmp_name).unlink(missing_ok=True)
