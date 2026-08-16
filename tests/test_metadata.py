"""Tests for project metadata, version parity, documentation and translations integrity."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import MethodenAnalyser3 as m3  # noqa: E402


def test_version_parity_across_artifacts():
    """Verify version numbers are consistent across code, pyproject, and store config."""
    # Check MethodenAnalyser3
    assert hasattr(m3, "TOOL_VERSION")
    assert hasattr(m3, "__version__")
    assert m3.TOOL_VERSION == "3.0"
    assert m3.__version__ == "3.0.0"

    # Check pyproject.toml
    pyproject_path = ROOT / "pyproject.toml"
    assert pyproject_path.exists(), "pyproject.toml must exist"
    pyproject_text = pyproject_path.read_text(encoding="utf-8")
    assert 'version = "3.0.0"' in pyproject_text

    # Check store_package.json
    store_pkg_path = ROOT / "store_package.json"
    if store_pkg_path.exists():
        store_data = json.loads(store_pkg_path.read_text(encoding="utf-8"))
        assert store_data.get("version", "").startswith("3.0.0")

    # Check CHANGELOG.md references version 3.0
    changelog_path = ROOT / "CHANGELOG.md"
    assert changelog_path.exists()
    changelog_text = changelog_path.read_text(encoding="utf-8")
    assert "3.0" in changelog_text


def test_required_documentation_files_exist():
    """Verify all standard docs and metadata files exist."""
    required_files = [
        "README.md",
        "README_de.md",
        "llms.txt",
        "CHANGELOG.md",
        "LICENSE",
        "PRIVACY_POLICY.md",
        "EXPORTFORMAT.md",
        "WEBAPP.md",
        "BUILD.md",
        "pyproject.toml",
    ]
    for rel_name in required_files:
        p = ROOT / rel_name
        assert p.is_file(), f"Required file missing: {rel_name}"
        assert p.stat().st_size > 0, f"File is empty: {rel_name}"


def test_llms_txt_integrity():
    """Verify llms.txt contains canonical links, sections and required metadata."""
    llms_path = ROOT / "llms.txt"
    assert llms_path.exists()
    content = llms_path.read_text(encoding="utf-8")

    assert "# MethodenAnalyser" in content
    assert "https://github.com/dev-bricks/MethodenAnalyser" in content
    assert "## Canonical Links" in content
    assert "## What It Does" in content
    assert "## Interfaces" in content
    assert "## Data And Privacy" in content
    assert "## Verification" in content
    assert "Last-checked:" in content


def test_translations_parity_and_validity():
    """Verify translations.json exists, is valid JSON and has parity between de and en."""
    trans_path = ROOT / "locales" / "translations.json"
    assert trans_path.exists()
    data = json.loads(trans_path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)

    for key, val in data.items():
        assert isinstance(val, dict), f"Key {key} must contain a dict with languages"
        assert "de" in val, f"Key {key} missing 'de' translation"
        assert "en" in val, f"Key {key} missing 'en' translation"
        assert len(val["de"]) > 0, f"Empty 'de' translation for {key}"
        assert len(val["en"]) > 0, f"Empty 'en' translation for {key}"


def test_export_format_constants():
    """Verify JSON schema version and report constants."""
    assert m3.JSON_SCHEMA_VERSION == "methodenanalyser-report-v1"
    assert m3.DEFAULT_JSON_REPORT_NAME == "methodenanalyser-report-v1.json"
    assert m3.EXIT_OK == 0
    assert m3.EXIT_ANALYSIS_ERROR == 1
    assert m3.EXIT_FINDINGS == 2
    assert m3.EXIT_PARTIAL_ERROR == 3
