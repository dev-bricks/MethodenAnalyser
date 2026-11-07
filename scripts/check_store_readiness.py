"""Validate repository-owned and external Windows Store readiness materials for MethodenAnalyser.

Repository-owned materials are checked in ``project_root``. Build and review
evidence can be supplied explicitly via ``--evidence-root`` for full release gate validation.
"""

from __future__ import annotations

import argparse
import json
import re
import tomllib
import zipfile
from pathlib import Path
from typing import Sequence
import xml.etree.ElementTree as ET


REQUIRED_DOCUMENTS = (
    "PRIVACY_POLICY.md",
    "SUPPORT.md",
    "STORE_LISTING.md",
    "WINDOWS_STORE_PREP.md",
    "PORTIERUNGSPLAN.md",
    "THIRD_PARTY_LICENSES.txt",
)

PASS_MARKERS = {
    "fulltrust-review.txt": "STATUS: PASS",
    "windows-tray-smoke.txt": "STATUS: PASS",
    "live-url-readback.txt": "STATUS: PASS",
    "msix-signature.txt": "SIGNATURE STATUS: PASS",
    "wack-report.txt": "OVERALL RESULT: PASS",
}

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

EXPECTED_TIER2_LANGS = ("de-DE", "en-US", "es-ES", "zh-CN", "ja-JP", "ru-RU")
BANNED_TRADEMARKS = {"windows", "microsoft", "google", "apple", "adobe", "pycharm", "vscode"}

REQUIRED_TILE_ICONS = {
    "icon_44x44.png": (44, 44),
    "icon_50x50.png": (50, 50),
    "icon_150x150.png": (150, 150),
    "icon_310x150.png": (310, 150),
    "icon_310x310.png": (310, 310),
}


def _read_nonempty(path: Path) -> str | None:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None
    return content if content.strip() else None


def _load_json(path: Path) -> dict[str, object] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _project_version(project_root: Path) -> str | None:
    try:
        data = tomllib.loads((project_root / "pyproject.toml").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError):
        pass
    else:
        project = data.get("project")
        if isinstance(project, dict):
            version = project.get("version")
            if isinstance(version, str) and version:
                return version

    # Fallback to MethodenAnalyser3.py
    main_py = project_root / "MethodenAnalyser3.py"
    if main_py.is_file():
        content = main_py.read_text(encoding="utf-8")
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)

    return None


def _check_repository(project_root: Path) -> list[str]:
    findings: list[str] = []
    config_path = project_root / "store_package.json"
    config = _load_json(config_path)
    if config is None:
        findings.append("[repository] store_package.json is missing or invalid")
    else:
        for field in ("publisher", "publisher_display", "identity_name", "version", "executable"):
            if not isinstance(config.get(field), str) or not str(config[field]).strip():
                findings.append(f"[repository] store_package.json field {field!r} is missing")

        app_name = config.get("name") or config.get("app_name")
        if not isinstance(app_name, str) or not app_name.strip():
            findings.append("[repository] store_package.json name/app_name is missing")

        for field in ("publisher", "publisher_display", "identity_name"):
            value = str(config.get(field, ""))
            if "your" in value.lower() or "placeholder" in value.lower():
                findings.append(f"[repository] store_package.json contains placeholder: {field}")

        for field in ("privacy_url", "support_url"):
            value = config.get(field)
            if not isinstance(value, str) or not value.startswith("https://"):
                findings.append(
                    f"[repository] store_package.json field {field!r} needs an HTTPS URL"
                )

        capabilities = config.get("capabilities")
        if isinstance(capabilities, list):
            if "runFullTrust" not in capabilities:
                findings.append("[repository] store_package.json must declare runFullTrust")
        elif isinstance(capabilities, str):
            if "runFullTrust" not in capabilities:
                findings.append("[repository] store_package.json must declare runFullTrust")
        else:
            findings.append("[repository] store_package.json capabilities missing or invalid")

        project_ver = _project_version(project_root)
        store_ver = str(config.get("version", ""))
        if not re.fullmatch(r"\d+\.\d+\.\d+\.\d+", store_ver):
            findings.append("[repository] store_package.json version must have 4 numeric parts")
        elif project_ver is not None and not store_ver.startswith(project_ver):
            findings.append(
                f"[repository] store version {store_ver!r} does not match project version {project_ver!r}"
            )

        declared_langs = config.get("languages")
        if not isinstance(declared_langs, list) or not all(lang in declared_langs for lang in EXPECTED_TIER2_LANGS):
            findings.append(
                f"[repository] store_package.json must declare all Tier-2 languages: {EXPECTED_TIER2_LANGS}"
            )

        for lang_code in ("de", "en", "es", "zh", "ja", "ru"):
            desc_key = f"description_{lang_code}"
            desc_val = config.get(desc_key)
            if not isinstance(desc_val, str) or not desc_val.strip():
                findings.append(f"[repository] store_package.json lacks {desc_key}")
            elif len(desc_val) > 100:
                findings.append(
                    f"[repository] store_package.json {desc_key} exceeds 100 characters ({len(desc_val)})"
                )

            kw_key = f"keywords_{lang_code}"
            kw_val = config.get(kw_key)
            if not isinstance(kw_val, list) or len(kw_val) != 7:
                findings.append(
                    f"[repository] store_package.json {kw_key} must contain exactly 7 keywords"
                )
            else:
                for kw in kw_val:
                    if not isinstance(kw, str) or not kw.strip():
                        findings.append(f"[repository] empty keyword in {kw_key}")
                    elif len(kw) > 30:
                        findings.append(f"[repository] keyword {kw!r} in {kw_key} exceeds 30 chars")
                    for b in BANNED_TRADEMARKS:
                        if b in kw.lower():
                            findings.append(f"[repository] banned trademark {b!r} in {kw_key}: {kw!r}")

    for doc in REQUIRED_DOCUMENTS:
        if _read_nonempty(project_root / doc) is None:
            findings.append(f"[repository] required document is missing or empty: {doc}")

    # Check AppxManifest.xml
    manifest_path = project_root / "store_package" / "MethodenAnalyser" / "AppxManifest.xml"
    if not manifest_path.is_file():
        findings.append("[repository] AppxManifest.xml is missing")
    else:
        try:
            tree = ET.parse(manifest_path)
            root_el = tree.getroot()
            ns = {"m": "http://schemas.microsoft.com/appx/manifest/foundation/windows10"}
            res_list = root_el.findall(".//m:Resources/m:Resource", ns)
            manifest_langs = {r.attrib.get("{http://schemas.microsoft.com/appx/manifest/foundation/windows10}Language", r.attrib.get("Language", "")).lower() for r in res_list}
            expected_manifest_langs = {"de-de", "en-us", "es-es", "zh-cn", "ja-jp", "ru-ru"}
            if not expected_manifest_langs.issubset(manifest_langs):
                findings.append(
                    f"[repository] AppxManifest.xml missing resource languages: {expected_manifest_langs - manifest_langs}"
                )
        except Exception as exc:
            findings.append(f"[repository] AppxManifest.xml parse error: {exc}")

    # Check tile icons in store_package/MethodenAnalyser/icons/
    icons_dir = project_root / "store_package" / "MethodenAnalyser" / "icons"
    if not icons_dir.is_dir():
        findings.append("[repository] store_package/MethodenAnalyser/icons directory is missing")
    else:
        for icon_name in REQUIRED_TILE_ICONS:
            icon_file = icons_dir / icon_name
            if not icon_file.is_file() or icon_file.stat().st_size < 100:
                findings.append(f"[repository] missing or invalid tile icon: {icon_name}")
            else:
                try:
                    data = icon_file.read_bytes()
                    if not data.startswith(PNG_SIGNATURE):
                        findings.append(f"[repository] tile icon {icon_name} is not a valid PNG")
                except OSError:
                    findings.append(f"[repository] tile icon {icon_name} cannot be read")

    # Check staging directory releases/windowsstore/
    staging_dir = project_root / "releases" / "windowsstore"
    if not staging_dir.is_dir():
        findings.append("[repository] releases/windowsstore directory is missing")
    else:
        for fname in ("store_settings.json", "BUILD.md", "WACK_PROTOCOL.md", "StoreLogo.png"):
            if not (staging_dir / fname).is_file():
                findings.append(f"[repository] releases/windowsstore lacks {fname}")
        for code in ("de", "en", "es", "zh", "ja", "ru"):
            listing_file = staging_dir / f"store_listing_{code}.md"
            if not listing_file.is_file() or listing_file.stat().st_size < 100:
                findings.append(
                    f"[repository] releases/windowsstore lacks valid store_listing_{code}.md"
                )

    # Check screenshots in releases/windowsstore/screenshots/
    screenshots: list[Path] = []
    screenshot_dirs = [
        staging_dir / "screenshots",
        staging_dir / "screenshots" / "de",
        staging_dir / "screenshots" / "en",
        project_root / "README" / "screenshots",
    ]
    for sdir in screenshot_dirs:
        if sdir.is_dir():
            for path in sdir.glob("*.png"):
                try:
                    if path.is_file() and path.read_bytes().startswith(PNG_SIGNATURE):
                        screenshots.append(path)
                except OSError:
                    continue

    if len(screenshots) < 3:
        findings.append(
            f"[repository] at least 3 valid PNG Store screenshots required; found {len(screenshots)}"
        )

    # Check translations.json parity
    trans_file = project_root / "locales" / "translations.json"
    if not trans_file.is_file():
        findings.append("[repository] locales/translations.json is missing")
    else:
        trans_data = _load_json(trans_file)
        if trans_data is None:
            findings.append("[repository] locales/translations.json is invalid JSON")
        else:
            expected_codes = {"de", "en", "es", "zh", "ja", "ru"}
            missing_parity = []
            for k, val in trans_data.items():
                if not isinstance(val, dict) or not expected_codes.issubset(val.keys()):
                    missing_parity.append(k)
            if missing_parity:
                findings.append(
                    f"[repository] translations.json missing language parity for {len(missing_parity)} keys"
                )

    return findings


def _check_evidence(evidence_root: Path | None) -> list[str]:
    if evidence_root is None:
        return [
            "[external] evidence root was not supplied (Partner Center reservation, FullTrust review, "
            "Windows tray smoke, live URL readback, SBOM, signed MSIX/hash, and WACK PASS remain open)"
        ]
    if not evidence_root.is_dir():
        return [f"[external] evidence root does not exist: {evidence_root}"]

    findings: list[str] = []
    for name, marker in PASS_MARKERS.items():
        content = _read_nonempty(evidence_root / name)
        if content is None or marker not in content:
            findings.append(f"[external] {name} is missing or lacks {marker!r}")

    packages = sorted(evidence_root.glob("*.msix"))
    if len(packages) != 1 or not zipfile.is_zipfile(packages[0]):
        findings.append(
            "[external] exactly one non-empty MSIX package with a ZIP header is required"
        )

    return findings


def collect_findings(project_root: Path, evidence_root: Path | None = None) -> list[str]:
    """Return all blocking repository and external Store-readiness findings."""
    return _check_repository(project_root.resolve()) + _check_evidence(
        evidence_root.resolve() if evidence_root is not None else None
    )


def validate() -> list[str]:
    """Backward-compatibility wrapper for repository validation."""
    root = Path(__file__).resolve().parents[1]
    return _check_repository(root)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="MethodenAnalyser source checkout (default: repository root)",
    )
    parser.add_argument(
        "--evidence-root",
        type=Path,
        help="External directory containing review, build, SBOM, hash, and WACK evidence",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    findings = _check_repository(args.project_root)
    if findings:
        print("STORE READINESS: BLOCKED")
        for finding in findings:
            print(f"- {finding}")
        return 1

    if args.evidence_root is not None:
        external_findings = _check_evidence(args.evidence_root)
        if external_findings:
            print("STORE READINESS: BLOCKED (EXTERNAL EVIDENCE)")
            for finding in external_findings:
                print(f"- {finding}")
            return 1
        print("STORE READINESS: FULLY RELEASE READY")
        return 0

    print("STORE READINESS: METADATA & REPOSITORY STAGED")
    print("External gates remain: Partner Center reservation, signed MSIX, and WACK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
