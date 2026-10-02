"""Automated Security, Dependency Vulnerability Floor, and License Contract Tests for MethodenAnalyser."""

from __future__ import annotations

import ast
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dependency_security_minimum_floors() -> None:
    """Ensure declared dependency version floors in pyproject.toml and requirements-dev.txt meet secure baselines."""
    pyproject_path = ROOT / "pyproject.toml"
    assert pyproject_path.exists(), "pyproject.toml must exist"

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    # Runtime dependencies must remain empty (pure Python standard library)
    runtime_deps = data["project"].get("dependencies", [])
    assert runtime_deps == [], f"MethodenAnalyser must have 0 runtime dependencies, found: {runtime_deps}"

    opt_deps = data["project"].get("optional-dependencies", {})
    dev_deps = opt_deps.get("dev", [])
    build_deps = opt_deps.get("build", [])

    dep_map: dict[str, str] = {}
    for spec in dev_deps + build_deps:
        match = re.match(r"^([a-zA-Z0-9_\-\[\]]+)\s*>=?\s*([0-9\.]+)", spec)
        if match:
            raw_name = match.group(1).split("[")[0].lower()
            dep_map[raw_name] = match.group(2)

    # Security Floor Checks (OSV / CVE baseline validation)
    # pytest < 9.1.1 is vulnerable to CVE-2025-7117 / GHSA-6w46-j5rx-g56g
    assert "pytest" in dep_map, "pytest must be declared in dev optional-dependencies"
    pt_ver = tuple(int(x) for x in dep_map["pytest"].split("."))
    assert pt_ver >= (9, 1, 1), f"pytest floor {dep_map['pytest']} is below secure floor 9.1.1"

    # ruff >= 0.9.0
    assert "ruff" in dep_map, "ruff must be declared in dev optional-dependencies"
    rf_ver = tuple(int(x) for x in dep_map["ruff"].split("."))
    assert rf_ver >= (0, 9, 0), f"ruff floor {dep_map['ruff']} is below 0.9.0"

    # PyInstaller >= 6.10.0
    assert "pyinstaller" in dep_map, "pyinstaller must be declared in build optional-dependencies"
    pi_ver = tuple(int(x) for x in dep_map["pyinstaller"].split("."))
    assert pi_ver >= (6, 10, 0), f"pyinstaller floor {dep_map['pyinstaller']} is below 6.10.0"

    # altgraph >= 0.17.4
    assert "altgraph" in dep_map, "altgraph must be declared in build optional-dependencies"
    ag_ver = tuple(int(x) for x in dep_map["altgraph"].split("."))
    assert ag_ver >= (0, 17, 4), f"altgraph floor {dep_map['altgraph']} is below 0.17.4"

    # packaging >= 24.0
    assert "packaging" in dep_map, "packaging must be declared in build optional-dependencies"
    pkg_ver = tuple(int(x) for x in dep_map["packaging"].split("."))
    assert pkg_ver >= (24, 0), f"packaging floor {dep_map['packaging']} is below 24.0"

    # Check requirements-dev.txt parity
    req_dev_path = ROOT / "requirements-dev.txt"
    assert req_dev_path.exists(), "requirements-dev.txt must exist"
    req_dev_text = req_dev_path.read_text(encoding="utf-8")
    assert "pytest>=9.1.1" in req_dev_text, "requirements-dev.txt must require pytest>=9.1.1"
    assert "ruff>=0.9.0" in req_dev_text, "requirements-dev.txt must require ruff>=0.9.0"


def test_third_party_license_inventory_completeness() -> None:
    """Verify THIRD_PARTY_LICENSES.txt covers all components using the standard 5-field schema."""
    license_file = ROOT / "THIRD_PARTY_LICENSES.txt"
    assert license_file.exists(), "THIRD_PARTY_LICENSES.txt must exist"
    content = license_file.read_text(encoding="utf-8").lower()

    # 5-field schema markers
    assert "package:" in content
    assert "license:" in content
    assert "spdx:" in content
    assert "url:" in content
    assert "notice:" in content

    # Runtime standard library attestations
    assert "package: python-stdlib" in content
    assert "package: tkinter" in content

    # Tooling and build packages
    expected_tooling = [
        "pytest",
        "pluggy",
        "iniconfig",
        "ruff",
        "pyinstaller",
        "pyinstaller-hooks-contrib",
        "altgraph",
        "packaging",
        "setuptools",
        "webapp-runtime",
    ]
    for pkg in expected_tooling:
        assert f"package: {pkg}" in content, f"Toolchain/companion dependency {pkg} missing from 5-field inventory"


def test_security_policy_bilingual_and_contacts() -> None:
    """Verify SECURITY.md provides bilingual reporting instructions, verified contact endpoints, and SLAs."""
    sec_path = ROOT / "SECURITY.md"
    assert sec_path.exists(), "SECURITY.md must exist"
    content = sec_path.read_text(encoding="utf-8")

    # Bilingual structure
    assert "# Security Policy / Sicherheitsrichtlinie" in content
    assert "## English" in content
    assert "## Deutsch" in content

    # SLAs
    assert "48 hours" in content or "48 Stunden" in content
    assert "5 business days" in content or "5 Werktage" in content

    # Private Vulnerability Reporting URL
    assert "https://github.com/dev-bricks/MethodenAnalyser/security/advisories/new" in content

    # Verified security contacts
    assert "security@open-bricks.org" in content
    assert "security@ellmos.ai" in content
    assert "support@lukasgeiger.com" in content
    assert "lukas@open-bricks.org" in content


def test_repo_hygiene_and_gitignore_rules() -> None:
    """Verify .gitignore contains comprehensive patterns for secrets, credentials, locks, and test outputs."""
    gi_path = ROOT / ".gitignore"
    assert gi_path.exists(), ".gitignore must exist"
    content = gi_path.read_text(encoding="utf-8")

    # Secrets and credentials
    for pattern in ["secrets.*", ".env", "credentials.json", "token.json", "*.pem", "*.key", "*.crt", "*.pfx", "*.p12", "*.cer"]:
        assert pattern in content, f"Pattern {pattern} missing from .gitignore"

    # Test artifacts
    for pattern in ["pytest_out.txt", "pytest*.txt", ".pytest_cache/", ".coverage"]:
        assert pattern in content, f"Test artifact pattern {pattern} missing from .gitignore"

    # Multi-agent locks and cloud sync conflicts
    for pattern in ["LOCK", "LOCK.*", "*.lock", "LOCK*.txt", "*-conflict-*", "*.conflict"]:
        assert pattern in content, f"Lock/conflict pattern {pattern} missing from .gitignore"


def test_no_hardcoded_user_paths_or_plaintext_secrets() -> None:
    """Ensure no hardcoded user paths or plaintext secrets exist in tracked source code and configs."""
    user_path_pattern = re.compile(r"([a-zA-Z]:\\Users\\[a-zA-Z0-9_\-\\]+|/home/[a-zA-Z0-9_\-]+)", re.IGNORECASE)
    secret_pattern = re.compile(
        r"(?i)(api[_-]?key|token|bearer|auth[_-]?key)\s*[:=]\s*['\"][A-Za-z0-9_\-\.]{16,}['\"]"
    )

    scanned_files = [
        ROOT / "MethodenAnalyser3.py",
        ROOT / "manage_translations.py",
        ROOT / "translator.py",
        ROOT / "webapp" / "server.py",
        ROOT / "pyproject.toml",
        ROOT / "requirements.txt",
        ROOT / "requirements-dev.txt",
        ROOT / "THIRD_PARTY_LICENSES.txt",
        ROOT / "SECURITY.md",
    ]

    for file_path in scanned_files:
        assert file_path.exists(), f"File {file_path} must exist for hygiene scan"
        text = file_path.read_text(encoding="utf-8", errors="ignore")

        # Scan for user paths (allow pytest temp dir references if any in comments)
        matches = user_path_pattern.findall(text)
        filtered_matches = [m for m in matches if "AppData" not in m and "pytest" not in m]
        assert not filtered_matches, f"Found hardcoded user path in {file_path}: {filtered_matches}"

        # Scan for plaintext secrets
        secret_matches = secret_pattern.findall(text)
        assert not secret_matches, f"Found potential secret in {file_path}: {secret_matches}"


def test_license_parity_across_manifests() -> None:
    """Verify MIT license declaration parity across pyproject.toml, LICENSE, and documentation."""
    license_file = ROOT / "LICENSE"
    assert license_file.exists(), "LICENSE file must exist"
    license_text = license_file.read_text(encoding="utf-8")
    assert "MIT License" in license_text
    assert "Lukas Geiger" in license_text

    pyproject_path = ROOT / "pyproject.toml"
    pyproject_text = pyproject_path.read_text(encoding="utf-8")
    assert 'license = { text = "MIT" }' in pyproject_text
    assert '"License :: OSI Approved :: MIT License"' in pyproject_text

    for readme_name in ["README.md", "README_de.md"]:
        readme_path = ROOT / readme_name
        readme_text = readme_path.read_text(encoding="utf-8")
        assert "MIT" in readme_text, f"MIT License must be mentioned in {readme_name}"


def test_local_first_and_offline_invariants() -> None:
    """Verify local-first architecture, zero network egress, and loopback binding in the webapp helper."""
    # Webapp server loopback verification
    server_path = ROOT / "webapp" / "server.py"
    assert server_path.exists(), "webapp/server.py must exist"

    # Default server binding must be strictly 127.0.0.1 loopback
    from webapp.server import LOCAL_ONLY_HOSTS, build_arg_parser

    parser = build_arg_parser()
    default_host = parser.get_default("host")
    assert default_host == "127.0.0.1", f"Default host must be 127.0.0.1 loopback, got {default_host}"
    assert "127.0.0.1" in LOCAL_ONLY_HOSTS, "127.0.0.1 must be categorized as LOCAL_ONLY_HOSTS"

    # Core CLI / GUI analysis zero external network imports
    m3_path = ROOT / "MethodenAnalyser3.py"
    assert m3_path.exists(), "MethodenAnalyser3.py must exist"
    m3_text = m3_path.read_text(encoding="utf-8")

    # Assert no dynamic network client libraries in main application
    forbidden_net_libs = ["urllib.request", "requests", "httpx", "aiohttp", "socket.socket"]
    for net_lib in forbidden_net_libs:
        assert f"import {net_lib}" not in m3_text, f"Forbidden network import {net_lib} found in MethodenAnalyser3.py"


def test_ast_static_analysis_safe_execution() -> None:
    """Verify that source code analysis is strictly static via ast.parse without dynamic code execution."""
    m3_path = ROOT / "MethodenAnalyser3.py"
    with open(m3_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(m3_path))

    # Inspect call nodes: ensuring analyze_file uses ast.parse and never eval/exec
    called_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                called_names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                called_names.add(node.func.attr)

    assert "parse" in called_names, "MethodenAnalyser must utilize ast.parse for static analysis"
    # Neither eval nor exec should be called directly
    assert "eval" not in called_names, "Direct call to eval() found in source code"
    assert "exec" not in called_names, "Direct call to exec() found in source code"
