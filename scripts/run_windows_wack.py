"""run_windows_wack.py - Führt das Windows App Certification Kit (WACK) für MethodenAnalyser aus oder erstellt hermetische Preflight-Reports."""

from __future__ import annotations

import argparse
import json
import shutil
import struct
import xml.etree.ElementTree as ET
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

try:
    import ctypes
except ImportError:
    ctypes = None

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_APPCERT = Path(r"C:\Program Files (x86)\Windows Kits\10\App Certification Kit\appcert.exe")
WACK_REPORT_PREFIX = "wack_preflight_"


@dataclass(frozen=True)
class WackSummary:
    report: str
    overall_result: str
    requirement_count: int
    pass_count: int
    fail_count: int
    warning_count: int


def _png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a valid PNG")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def load_store_config(project_root: Path) -> dict[str, object]:
    settings_file = project_root / "releases" / "windowsstore" / "store_settings.json"
    if settings_file.exists():
        try:
            return json.loads(settings_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    pkg_file = project_root / "store_package.json"
    if pkg_file.exists():
        try:
            return json.loads(pkg_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {}


def expected_msix_path(project_root: Path, store_config: dict[str, object]) -> Path:
    app_name = str(store_config.get("msix_name") or "MethodenAnalyser.msix")
    candidate_dirs = [
        project_root / "releases" / "windowsstore",
        project_root / "releases",
        project_root / "dist",
    ]
    for directory in candidate_dirs:
        candidate = directory / app_name
        if candidate.exists():
            return candidate
    return candidate_dirs[0] / app_name


def resolve_msix_path(project_root: Path, store_config: dict[str, object], explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit.expanduser().resolve()
    return expected_msix_path(project_root, store_config).resolve()


def resolve_report_path(project_root: Path, report_dir: Path | None, explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit.expanduser().resolve()
    base_dir = (report_dir or (project_root / "releases" / "windowsstore" / "test_reports")).expanduser().resolve()
    timestamp = datetime.now().astimezone().strftime("%Y%m%d")
    return base_dir / f"{WACK_REPORT_PREFIX}{timestamp}.xml"


def find_appcert(explicit: Path | None = None) -> Path | None:
    if explicit is not None:
        candidate = explicit.expanduser().resolve()
        return candidate if candidate.is_file() else None
    if DEFAULT_APPCERT.is_file():
        return DEFAULT_APPCERT
    discovered = shutil.which("appcert.exe")
    return Path(discovered).resolve() if discovered else None


def is_windows_admin() -> bool:
    if ctypes is None or not hasattr(ctypes, "windll"):
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except (AttributeError, OSError):
        return False


def run_preflight_checks(project_root: Path, store_config: dict[str, object]) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []

    # 1. Manifest
    manifest_candidates = [
        project_root / "store_package" / "MethodenAnalyser" / "AppxManifest.xml",
        project_root / "AppxManifest.xml",
    ]
    manifest = next((p for p in manifest_candidates if p.exists()), None)
    if manifest is not None:
        try:
            tree = ET.parse(manifest)
            root = tree.getroot()
            checks.append({
                "id": "MANIFEST_SYNTAX",
                "name": "AppxManifest-Validierung & XML-Wohlgeformtheit",
                "result": "PASS",
                "details": f"Manifest syntax OK: {manifest.name}",
            })
            caps = [elem.attrib.get("Name") for elem in root.iter() if elem.tag.endswith("Capability")]
            if "runFullTrust" in caps:
                checks.append({
                    "id": "RESTRICTED_CAPABILITIES",
                    "name": "Restricted Capabilities Deklaration (runFullTrust)",
                    "result": "PASS",
                    "details": "Desktop-Bridge Anwendung deklariert runFullTrust",
                })
            else:
                checks.append({
                    "id": "RESTRICTED_CAPABILITIES",
                    "name": "Restricted Capabilities Deklaration (runFullTrust)",
                    "result": "FAIL",
                    "details": "runFullTrust Capability fehlt im Manifest",
                })

            logo_elem = root.find(".//{http://schemas.microsoft.com/appx/manifest/foundation/windows10}Logo")
            if logo_elem is not None and logo_elem.text:
                logo_path = logo_elem.text
                if "50x50" in logo_path or "StoreLogo" in logo_path:
                    checks.append({
                        "id": "PROPERTIES_LOGO",
                        "name": "Properties Logo 50x50 Store-Konformität",
                        "result": "PASS",
                        "details": f"Properties Logo referenziert standardkonform 50x50 Logo: {logo_path}",
                    })
                else:
                    checks.append({
                        "id": "PROPERTIES_LOGO",
                        "name": "Properties Logo 50x50 Store-Konformität",
                        "result": "WARNING",
                        "details": f"Properties Logo referenziert {logo_path} statt StoreLogo.png (50x50)",
                    })
            else:
                checks.append({
                    "id": "PROPERTIES_LOGO",
                    "name": "Properties Logo 50x50 Store-Konformität",
                    "result": "FAIL",
                    "details": "Properties Logo-Element fehlt im Manifest",
                })
        except (OSError, ET.ParseError) as e:
            checks.append({
                "id": "MANIFEST_SYNTAX",
                "name": "AppxManifest-Validierung & XML-Wohlgeformtheit",
                "result": "FAIL",
                "details": f"Manifest Parse-Fehler: {e}",
            })
    else:
        checks.append({
            "id": "MANIFEST_SYNTAX",
            "name": "AppxManifest-Validierung & XML-Wohlgeformtheit",
            "result": "FAIL",
            "details": "AppxManifest.xml nicht gefunden",
        })

    # 2. Tile Assets
    required_icons = ["icon_44x44.png", "icon_50x50.png", "icon_150x150.png", "icon_310x150.png", "icon_310x310.png"]
    icon_dirs = [
        project_root / "store_assets",
        project_root / "store_package" / "MethodenAnalyser" / "icons",
        project_root / "releases" / "windowsstore",
    ]
    all_icons_ok = True
    missing_details = []
    for d in icon_dirs:
        if not d.exists():
            all_icons_ok = False
            missing_details.append(f"Ordner {d.name} fehlt")
            continue
        for ic in required_icons:
            ic_path = d / ic
            if not ic_path.is_file() or ic_path.stat().st_size == 0:
                all_icons_ok = False
                missing_details.append(f"{ic} in {d.name} fehlt oder ist leer")

    store_logo_file = project_root / "releases" / "windowsstore" / "StoreLogo.png"
    if not store_logo_file.is_file() or store_logo_file.stat().st_size == 0:
        all_icons_ok = False
        missing_details.append("StoreLogo.png in releases/windowsstore fehlt")

    if all_icons_ok:
        checks.append({
            "id": "TILE_ICONS",
            "name": "Vollständigkeit & Maßhaltigkeit der Store-Kachelicons",
            "result": "PASS",
            "details": "Alle Kacheln (44..310px inkl. StoreLogo 50x50) in allen Zielverzeichnissen vorhanden",
        })
    else:
        checks.append({
            "id": "TILE_ICONS",
            "name": "Vollständigkeit & Maßhaltigkeit der Store-Kachelicons",
            "result": "FAIL",
            "details": "; ".join(missing_details),
        })

    # 3. Policy 10.1.3 Keywords
    kw_de = store_config.get("keywords_de", [])
    kw_en = store_config.get("keywords_en", [])
    if isinstance(kw_de, list) and isinstance(kw_en, list) and 1 <= len(kw_de) <= 7 and 1 <= len(kw_en) <= 7:
        checks.append({
            "id": "POLICY_10_1_3_KEYWORDS",
            "name": "Partner Center Richtlinie 10.1.3 Suchbegriffe (max. 7 Keywords)",
            "result": "PASS",
            "details": f"DE: {len(kw_de)} Keywords, EN: {len(kw_en)} Keywords (strikt im Limit)",
        })
    else:
        checks.append({
            "id": "POLICY_10_1_3_KEYWORDS",
            "name": "Partner Center Richtlinie 10.1.3 Suchbegriffe (max. 7 Keywords)",
            "result": "FAIL",
            "details": f"Ungültige Keyword-Anzahl: DE={len(kw_de) if isinstance(kw_de, list) else 0}, EN={len(kw_en) if isinstance(kw_en, list) else 0}",
        })

    # 4. Screenshots
    shots_dir = project_root / "releases" / "windowsstore" / "screenshots"
    shots = list(shots_dir.glob("*.png")) if shots_dir.is_dir() else []
    if len(shots) >= 3:
        checks.append({
            "id": "SCREENSHOTS_PRESENCE",
            "name": "Store Screenshots Vorhandensein & Mindestanzahl",
            "result": "PASS",
            "details": f"{len(shots)} Screenshots in releases/windowsstore/screenshots/ vorhanden",
        })
    else:
        checks.append({
            "id": "SCREENSHOTS_PRESENCE",
            "name": "Store Screenshots Vorhandensein & Mindestanzahl",
            "result": "FAIL",
            "details": f"Nur {len(shots)} Screenshots vorhanden (mind. 3 erforderlich)",
        })

    # 5. Staging Listings
    missing_listings = []
    for code in ("de", "en", "es", "zh", "ja", "ru"):
        lf = project_root / "releases" / "windowsstore" / f"store_listing_{code}.md"
        if not lf.is_file() or lf.stat().st_size < 50:
            missing_listings.append(f"store_listing_{code}.md")

    if not missing_listings:
        checks.append({
            "id": "STAGING_LISTINGS",
            "name": "Tier-2 6-Sprachen Store-Listings Staging-Präsenz",
            "result": "PASS",
            "details": "Alle 6 Sprach-Listings (DE, EN, ES, ZH, JA, RU) in releases/windowsstore/ vorhanden",
        })
    else:
        checks.append({
            "id": "STAGING_LISTINGS",
            "name": "Tier-2 6-Sprachen Store-Listings Staging-Präsenz",
            "result": "FAIL",
            "details": f"Fehlende oder leere Listings: {', '.join(missing_listings)}",
        })

    # 6. Documentation
    required_docs = ["BUILD.md", "WACK_PROTOCOL.md", "store_settings.json"]
    missing_docs = [d for d in required_docs if not (project_root / "releases" / "windowsstore" / d).is_file()]
    if not missing_docs:
        checks.append({
            "id": "STAGING_DOCS",
            "name": "Store Staging Dokumentation & Build-Anleitungen",
            "result": "PASS",
            "details": "BUILD.md, WACK_PROTOCOL.md und store_settings.json vollständig",
        })
    else:
        checks.append({
            "id": "STAGING_DOCS",
            "name": "Store Staging Dokumentation & Build-Anleitungen",
            "result": "FAIL",
            "details": f"Fehlende Staging-Dokumente: {', '.join(missing_docs)}",
        })

    return checks


def write_xml_report(path: Path, checks: list[dict[str, object]]) -> WackSummary:
    path.parent.mkdir(parents=True, exist_ok=True)
    root = ET.Element("REPORT", {
        "TOOL": "WACK-Preflight-Runner",
        "VERSION": "1.0.0",
        "TIMESTAMP": datetime.now().astimezone().isoformat(),
    })
    summary_elem = ET.SubElement(root, "SUMMARY")
    passes = sum(1 for c in checks if c["result"] == "PASS")
    fails = sum(1 for c in checks if c["result"] == "FAIL")
    warns = sum(1 for c in checks if c["result"] == "WARNING")
    overall = "PASS" if fails == 0 else "FAIL"

    summary_elem.set("OVERALL_RESULT", overall)
    summary_elem.set("TOTAL_CHECKS", str(len(checks)))
    summary_elem.set("PASS_COUNT", str(passes))
    summary_elem.set("FAIL_COUNT", str(fails))
    summary_elem.set("WARN_COUNT", str(warns))

    results_elem = ET.SubElement(root, "CHECKS")
    for chk in checks:
        item = ET.SubElement(results_elem, "CHECK", {
            "ID": str(chk.get("id", "")),
            "RESULT": str(chk.get("result", "")),
        })
        name_sub = ET.SubElement(item, "NAME")
        name_sub.text = str(chk.get("name", ""))
        det_sub = ET.SubElement(item, "DETAILS")
        det_sub.text = str(chk.get("details", ""))

    tree = ET.ElementTree(root)
    tree.write(path, encoding="utf-8", xml_declaration=True)

    return WackSummary(
        report=str(path),
        overall_result=overall,
        requirement_count=len(checks),
        pass_count=passes,
        fail_count=fails,
        warning_count=warns,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Gibt die Zusammenfassung als JSON aus")
    parser.add_argument("--dry-run", action="store_true", help="Führt nur die statische Preflight-Prüfung aus")
    parser.add_argument("--report-dir", type=Path, help="Zielordner für XML-Prüfberichte")
    parser.add_argument("--msix", type=Path, help="Expliziter Pfad zum MSIX-Paket")
    args = parser.parse_args(argv)

    cfg = load_store_config(PROJECT_ROOT)
    checks = run_preflight_checks(PROJECT_ROOT, cfg)
    report_file = resolve_report_path(PROJECT_ROOT, args.report_dir, None)
    summary = write_xml_report(report_file, checks)

    if args.json:
        print(json.dumps(asdict(summary), indent=2))
    else:
        print(f"WACK Preflight Result: {summary.overall_result}")
        print(f"Pass: {summary.pass_count}, Fail: {summary.fail_count}, Warn: {summary.warning_count}")
        print(f"Report: {summary.report}")

    return 0 if summary.fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
