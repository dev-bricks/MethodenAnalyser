# CROSSCHECK — Externe Dependencies

> Vorlage: `_TEMPLATES/CROSSCHECK_TEMPLATE.md` | Konvention: GUIDE.md §Toolchain-Standards
> Pfad: `_sources/CROSSCHECK.md` im jeweiligen Projektordner
> Stand: 2026-08-26

## Projektübersicht

- **Projekt:** MethodenAnalyser v3.0.0
- **Python:** >=3.10 (getestet: 3.10, 3.11, 3.12)
- **Runtime-Dependencies:** Keine — ausschließlich Python-Standardbibliothek

## Verwendete Pakete mit Major-Version-Pinning

### Runtime-Dependencies

Keine externen Pakete. Der MethodenAnalyser nutzt ausschließlich die Python-Standardbibliothek:

| Modul | Typ | Anmerkung |
|---|---|---|
| tkinter | stdlib | GUI (Tk-Binding, bei Python-Installation enthalten) |
| argparse | stdlib | CLI-Parsing |
| ast | stdlib | Python-AST-Analyse |
| re | stdlib | Regex |
| json | stdlib | JSON-Verarbeitung |
| sqlite3 | stdlib | Datenbank |
| pathlib | stdlib | Pfadverarbeitung |
| collections | stdlib | Counter, defaultdict |
| difflib | stdlib | Ähnlichkeitserkennung |
| threading | stdlib | Hintergrundverarbeitung |
| dataclasses | stdlib | Datenklassen |
| http.server | stdlib | WebApp-Server |

### Dev-/Build-Dependencies (nicht für Runtime erforderlich)

| Paket | Vertrag | Smoke-Version | Letzte Prüfung | Verwendung |
|---|---|---|---|---|
| pytest | `>=9.0.3,<10.0` | 9.1.1 | 2026-08-26 | Lokaler Testlauf |
| pyinstaller | `>=6.14.2,<7.0` | 6.21.0 | 2026-08-26 | EXE-/MSIX-Build |

> **Hinweis:** Die CI (GitHub Actions) verwendet `python -m unittest` ohne externe Dependencies.
> pytest und pyinstaller werden nur lokal für Entwicklung und Release-Builds benötigt.

Installation des reproduzierbaren Dev-/Build-Vertrags: `python -m pip install -r requirements-dev.txt`.
Die konkrete Smoke-Ausführung dokumentiert zusätzlich die tatsächlich installierten
Versionen; eine Installation außerhalb dieses Bereichs ist kein verifizierter Build.

Aktuelle Version prüfen: `python -m pip show pytest pyinstaller` oder `pip list --outdated`.

## Reproduzierbarer Build-/Testvertrag

- Runtime: ausschließlich Python-Standardbibliothek, Python 3.10/3.11/3.12 in
  der CI-Matrix; `tkinter` ist eine Voraussetzung der jeweiligen Python-Installation.
- Tests: `python -m unittest discover -s tests -v` (keine pytest-Plugins im CI).
- EXE: `build_exe.bat` ruft `python -m PyInstaller` direkt für
  `MethodenAnalyser3.py` mit `--windowed --onefile` auf; die eingecheckte
  `MethodenAnalyser.spec` wird von diesem Batch-Pfad nicht eingelesen. Der
  optionale zentrale Exclude-Scanner wird verwendet, wenn er vorhanden ist;
  fehlt er, läuft der dokumentierte Fallback ohne dynamische Excludes.
- Build-Ausgabe: Primär
  `C:\_Local_DEV\codex_build\methodenanalyser\dist\MethodenAnalyser.exe`, danach
  Kopien nach `dist\MethodenAnalyser.exe` und `MethodenAnalyser.exe` im Projekt.
  Diese lokalen Artefakte sind kein Release und werden nicht automatisch in
  `releases/` veröffentlicht.
- Store/MSIX: Die Store-Vorbereitung bleibt ein separater, manuell freizugebender
  Schritt; dieser Vertrag führt keinen Signier-, Upload- oder WACK-Lauf aus.

---

## P0 — Sicherheit / CVEs (blockiert Release)

| # | Paket | Problem | Status | Behoben in |
|---|---|---|---|---|
| — | — | Keine bekannten Probleme | — | — |

Quellen: [PyPI Safety DB](https://pypi.org/), [CVE MITRE](https://cve.mitre.org/), `safety check`

---

## P1 — Breaking Changes bei Major-Update (dokumentieren vor Update)

| # | Paket | Von | Nach | Breaking Change | Aufwand |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

---

## P2 — Deprecation-Warnings

| # | Paket | Warnung | Deadline | Maßnahme |
|---|---|---|---|---|
| — | — | — | — | — |

---

## P3 — Nice-to-have Features / Performance

| # | Paket | Neue Funktion | Nützlich für | Priorität |
|---|---|---|---|---|
| — | — | — | — | niedrig |

---

## Workflow

1. **Vor jedem Release:** Alle P0-Einträge abarbeiten; P1 dokumentiert und im CHANGELOG vermerkt.
2. **Quartalsmäßig:** `uv pip list --outdated` laufen lassen, Tabelle aktualisieren.
3. **Neue Deps:** Direkt beim Hinzufügen einen P2/P3-Eintrag anlegen, falls relevante Breaking-Change-Noten im Changelog.
