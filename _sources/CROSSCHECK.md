# CROSSCHECK — Externe Dependencies

> Vorlage: `_TEMPLATES/CROSSCHECK_TEMPLATE.md` | Konvention: GUIDE.md §Toolchain-Standards
> Pfad: `_sources/CROSSCHECK.md` im jeweiligen Projektordner
> Stand: 2026-06-07

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

| Paket | Gepinnte Version | Aktuelle Version | Letzte Prüfung | Verwendung |
|---|---|---|---|---|
| pytest | nicht gepinnt | 9.0.3 | 2026-06-07 | Lokaler Testlauf |
| pyinstaller | nicht gepinnt | 6.14.2 | 2026-06-07 | EXE-/MSIX-Build |

> **Hinweis:** Die CI (GitHub Actions) verwendet `python -m unittest` ohne externe Dependencies.
> pytest und pyinstaller werden nur lokal für Entwicklung und Release-Builds benötigt.

Aktuelle Version prüfen: `python -m uv pip list --outdated` oder `pip list --outdated`

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
