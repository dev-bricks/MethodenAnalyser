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
    assert m3.__version__ == "3.0.2"

    # Check pyproject.toml
    pyproject_path = ROOT / "pyproject.toml"
    assert pyproject_path.exists(), "pyproject.toml must exist"
    pyproject_text = pyproject_path.read_text(encoding="utf-8")
    assert 'version = "3.0.2"' in pyproject_text

    # Check store_package.json
    store_pkg_path = ROOT / "store_package.json"
    if store_pkg_path.exists():
        store_data = json.loads(store_pkg_path.read_text(encoding="utf-8"))
        assert store_data.get("version", "").startswith("3.0.2")

    # Check CHANGELOG.md references version 3.0.2
    changelog_path = ROOT / "CHANGELOG.md"
    assert changelog_path.exists()
    changelog_text = changelog_path.read_text(encoding="utf-8")
    assert "3.0.2" in changelog_text


def test_required_documentation_files_exist():
    """Verify all standard docs and metadata files exist."""
    required_files = [
        "README.md",
        "README_de.md",
        "llms.txt",
        "CHANGELOG.md",
        "LICENSE",
        "SECURITY.md",
        "PRIVACY_POLICY.md",
        "EXPORTFORMAT.md",
        "WEBAPP.md",
        "BUILD.md",
        "THIRD_PARTY_LICENSES.md",
        "MARKETING-LOG.txt",
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
    """Verify translations.json exists, is valid JSON and has parity across all 6 languages."""
    trans_path = ROOT / "locales" / "translations.json"
    assert trans_path.exists()
    data = json.loads(trans_path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)

    for key, val in data.items():
        assert isinstance(val, dict), f"Key {key} must contain a dict with languages"
        for lang in ("de", "en", "es", "zh", "ja", "ru"):
            assert lang in val, f"Key {key} missing '{lang}' translation"
            assert len(val[lang].strip()) > 0, f"Empty '{lang}' translation for {key}"


def test_export_format_constants():
    """Verify JSON schema version and report constants."""
    assert m3.JSON_SCHEMA_VERSION == "methodenanalyser-report-v1"
    assert m3.DEFAULT_JSON_REPORT_NAME == "methodenanalyser-report-v1.json"
    assert m3.EXIT_OK == 0
    assert m3.EXIT_ANALYSIS_ERROR == 1
    assert m3.EXIT_FINDINGS == 2
    assert m3.EXIT_PARTIAL_ERROR == 3


def test_pep621_metadata_and_project_urls():
    """Verify pyproject.toml adheres to PEP 621 with full URLs and classifiers."""
    pyproject_path = ROOT / "pyproject.toml"
    assert pyproject_path.exists()
    content = pyproject_path.read_text(encoding="utf-8")

    # Project URLs
    assert "[project.urls]" in content
    expected_urls = [
        'Homepage = "https://github.com/dev-bricks/MethodenAnalyser"',
        'Documentation = "https://github.com/dev-bricks/MethodenAnalyser#readme"',
        'Repository = "https://github.com/dev-bricks/MethodenAnalyser"',
        'Issues = "https://github.com/dev-bricks/MethodenAnalyser/issues"',
        'Changelog = "https://github.com/dev-bricks/MethodenAnalyser/blob/master/CHANGELOG.md"',
        'Security = "https://github.com/dev-bricks/MethodenAnalyser/blob/master/SECURITY.md"',
        'Umbrella = "https://github.com/open-bricks/open-bricks"',
        'Parent-Organization = "https://github.com/dev-bricks"',
        'Marketing-Log = "https://github.com/dev-bricks/MethodenAnalyser/blob/master/MARKETING-LOG.txt"',
        'Third-Party-Licenses = "https://github.com/dev-bricks/MethodenAnalyser/blob/master/THIRD_PARTY_LICENSES.md"',
    ]
    for url_entry in expected_urls:
        assert url_entry in content, f"Missing URL entry: {url_entry}"

    # Classifiers
    for py_ver in ["3.10", "3.11", "3.12", "3.13"]:
        assert f'"Programming Language :: Python :: {py_ver}"' in content

    for os_target in [
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
    ]:
        assert f'"{os_target}"' in content

    # Entrypoints
    assert "[project.scripts]" in content
    assert 'methodenanalyser = "MethodenAnalyser3:main"' in content
    assert "[project.gui-scripts]" in content
    assert 'methodenanalyser-gui = "MethodenAnalyser3:main"' in content


def test_security_policy_bilingual_and_invariants():
    """Verify SECURITY.md contains bilingual policy, guarantees and reporting channels."""
    sec_path = ROOT / "SECURITY.md"
    assert sec_path.exists()
    content = sec_path.read_text(encoding="utf-8")

    # Bilingual navigation and sections
    assert "# Security Policy / Sicherheitsrichtlinie" in content
    assert "[English](#english)" in content
    assert "[Deutsch](#deutsch)" in content
    assert '<a name="english"></a>' in content
    assert '<a name="deutsch"></a>' in content

    # Security guarantees & invariants
    assert "Local-First & Zero Network Egress" in content
    assert "Local-First & Zero-Egress" in content
    assert "Read-Only Source Code Analysis" in content
    assert "Schreibschutz bei Analysen" in content
    assert "Inert Static Analysis" in content
    assert "Inerte statische Analyse" in content
    assert "Unprivileged User-Mode Execution" in content
    assert "Ausführung mit Benutzerrechten" in content

    # Supported versions and reporting channels
    assert "| 3.0.x   | :white_check_mark: |" in content
    assert "https://github.com/dev-bricks/MethodenAnalyser/security/advisories/new" in content
    assert "security@open-bricks.org" in content
    assert "security@ellmos.ai" in content
    assert "support@lukasgeiger.com" in content
    assert "lukas@open-bricks.org" in content

    # SLA commitments
    assert "48 hours" in content
    assert "48 Stunden" in content
    assert "5 business days" in content
    assert "5 Werktagen" in content


def test_ci_workflow_matrix_and_concurrency():
    """Verify CI workflow tests.yml includes concurrency, Python 3.13 and multi-OS runners."""
    ci_path = ROOT / ".github" / "workflows" / "tests.yml"
    assert ci_path.exists()
    content = ci_path.read_text(encoding="utf-8")

    # Concurrency
    assert "concurrency:" in content
    assert "cancel-in-progress: true" in content

    # Matrix coverage
    assert 'python-version: "3.10"' in content
    assert 'python-version: "3.11"' in content
    assert 'python-version: "3.12"' in content
    assert 'python-version: "3.13"' in content

    # Runner targets
    assert "windows-2025-vs2026" in content
    assert "ubuntu-latest" in content
    assert "macos-26" in content

    # Steps
    assert "pytest -ra -v" in content
    assert "ruff check ." in content
    assert "python -m compileall -q ." in content


def test_readme_quick_navigation_and_anchor_parity():
    """Verify both README.md and README_de.md contain quick navigation bars and valid anchors."""
    for filename in ["README.md", "README_de.md"]:
        readme_path = ROOT / filename
        assert readme_path.exists()
        content = readme_path.read_text(encoding="utf-8")

        # Quick navigation bar exists
        assert '<p align="center">' in content

        # Check key navigation targets exist in document
        assert "#features" in content
        assert "#architecture" in content or "#architektur" in content
        assert "#governance" in content
        assert "#screenshot" in content
        assert "#installation" in content
        assert "#exit-codes" in content


def test_readme_dual_mermaid_diagrams():
    """Verify both READMEs include dual Mermaid diagrams: flowchart TD and sequenceDiagram."""
    for filename in ["README.md", "README_de.md"]:
        readme_path = ROOT / filename
        content = readme_path.read_text(encoding="utf-8")

        # Flowchart architecture
        assert "```mermaid" in content
        assert "flowchart TD" in content

        # Sequence diagram lifecycle
        assert "sequenceDiagram" in content
        assert "autonumber" in content


def test_readme_governance_invariants_table():
    """Verify both READMEs define the 10 Governance and Runtime Invariants."""
    for filename in ["README.md", "README_de.md"]:
        readme_path = ROOT / filename
        content = readme_path.read_text(encoding="utf-8")

        for inv_id in [
            "INV-LOCAL-01",
            "INV-SECURITY-02",
            "INV-AST-03",
            "INV-ENCODING-04",
            "INV-ISOLATION-05",
            "INV-TRAVERSAL-06",
            "INV-AUTOFIX-07",
            "INV-PLATFORM-08",
            "INV-SYNC-09",
            "INV-SLA-10",
        ]:
            assert inv_id in content, f"{inv_id} missing in {filename}"


def test_readme_sibling_ecosystem_matrix():
    """Verify both READMEs include sibling ecosystem tools across partner orgs."""
    for filename in ["README.md", "README_de.md"]:
        readme_path = ROOT / filename
        content = readme_path.read_text(encoding="utf-8")

        for partner in [
            "DevCenter",
            "CodeBox",
            "CareCenter-for-Codex",
            "lock-master",
            "clutch",
            "assistant-core",
            "decision-clicker",
            "policy-registry",
            "ellmos-codecommander-mcp",
            "ellmos-filecommander-mcp",
            "ExplorerPro",
            "ProFiler",
            "FormularErstellen",
            "open-bricks",
        ]:
            assert partner in content, f"{partner} missing in {filename}"


def test_gitignore_lock_and_conflict_rules():
    """Verify .gitignore ignores multi-agent lock patterns and cloud sync conflict files."""
    gi_path = ROOT / ".gitignore"
    assert gi_path.exists()
    content = gi_path.read_text(encoding="utf-8")

    # Locks
    assert "LOCK" in content
    assert "LOCK.*" in content
    assert "*.lock" in content
    assert "LOCK.permissions.json" in content
    assert "!LOCK.md" in content

    # Conflicts
    assert "*-conflict-*" in content
    assert "*-WORKSTATION-LG*" in content
    assert "*-ASUS-GEI*" in content


def test_third_party_licenses_document():
    """Verify THIRD_PARTY_LICENSES.md declares zero external runtime dependencies."""
    tpl_path = ROOT / "THIRD_PARTY_LICENSES.md"
    assert tpl_path.exists()
    content = tpl_path.read_text(encoding="utf-8")

    assert "Zero External Dependencies" in content
    assert "ast" in content
    assert "tkinter" in content
    assert "difflib" in content
    assert "MIT License" in content


def test_marketing_log_integrity():
    """Verify MARKETING-LOG.txt documents discoverability, keywords and audience segmentation."""
    ml_path = ROOT / "MARKETING-LOG.txt"
    assert ml_path.exists()
    content = ml_path.read_text(encoding="utf-8")

    assert "MARKETING & DISCOVERABILITY LOG" in content
    assert "dev-bricks/MethodenAnalyser" in content
    assert "AUDIENCE SEGMENTATION" in content
    assert "DISCOVERABILITY KEYWORDS" in content
    assert "GOVERNANCE & RUNTIME INVARIANTS" in content


def test_pytest_configuration_flags():
    """Verify pyproject.toml defines standardized -ra -v pytest addopts."""
    pyproject_path = ROOT / "pyproject.toml"
    assert pyproject_path.exists()
    content = pyproject_path.read_text(encoding="utf-8")
    assert '[tool.pytest.ini_options]' in content
    assert 'addopts = "-ra -v"' in content


def test_changelog_recent_pfad_a_entry():
    """Verify CHANGELOG.md contains the 3.0.2 release notes with Pfad A hygiene entries."""
    cl_path = ROOT / "CHANGELOG.md"
    assert cl_path.exists()
    content = cl_path.read_text(encoding="utf-8")
    assert "## [3.0.2] - 2026-09-11" in content
    assert "Pfad A" in content
    assert "Versionsharmonisierung (v3.0.2)" in content


def test_extended_gitignore_patterns():
    """Verify .gitignore contains extended lock, conflict, and cache patterns."""
    gi_path = ROOT / ".gitignore"
    assert gi_path.exists()
    content = gi_path.read_text(encoding="utf-8")
    assert "uv.lock" in content
    assert "*-WORKSTATION*" in content
    assert "* (kopie)*" in content
    assert "* (copy)*" in content
    assert ".coverage.*" in content
    assert ".wheel-smoke/" in content
    assert "wheelhouse/" in content


def test_marketing_log_recent_hygiene_entry():
    """Verify MARKETING-LOG.txt includes the 2026-09-11 Pfad A audit log."""
    ml_path = ROOT / "MARKETING-LOG.txt"
    assert ml_path.exists()
    content = ml_path.read_text(encoding="utf-8")
    assert "[2026-09-11] PFAD A TECHNICAL HYGIENE" in content
    assert "v3.0.2" in content
    assert "GITHUBBOT_ONE_REPO_CLEANER (Pfad A)" in content
