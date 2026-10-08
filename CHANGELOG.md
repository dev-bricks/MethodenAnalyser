# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### CLI Windows cp1252-Resilienz & Tier-2 Translations-Paritäts-Tooling (2026-10-09)
- **Windows cp1252 CLI Encoding-Resilienz (`MethodenAnalyser3.py`)**:
  - `generate_report`: Unicode-Pfeil `\u2192` (`→`) bei der Ausgabe ähnlicher Namens-Matches (`name_matches`) durch ASCII-Pfeil `->` ersetzt. Behebt `BS-02-BACKLOG` und schließt `UnicodeEncodeError: 'charmap' codec can't encode character '\u2192'` auf Windows-Konsolen mit Standard-Codepage cp1252 zuverlässig aus.
  - `_emit_cli_report`: Defensive Encoding-Behandlung für `sys.stdout` integriert. Fängt eventuelle `UnicodeEncodeError` zur Laufzeit ab und gibt sanitisierten Text mit `errors="replace"` aus, um unberechtigte CLI-Abstürze bei restriktiven Terminal-Encodings auszuschließen.
- **Tier-2 6-Sprachen-Paritäts-Tooling (`manage_translations.py`)**:
  - `manage_translations.py` um `--check` Flag erweitert (verifiziert 100% Schlüsselparität über alle 6 unterstützten Sprachen DE, EN, ES, ZH, JA, RU und liefert Exit-Code 0 bei Erfolg, 1 bei Fehlern).
  - `--stats` Flag zur transparenten Anzeige von Gesamtbestand und prozentualem Deckungsgrad je Sprache ergänzt (183/183 Schlüssel, 100% Parität).
  - Vollständige Abwärtskompatibilität für das Scannen und Hinzufügen neuer deutscher Strings beibehalten.
- **Automatisierte Vertragstests (`tests/test_bugsweep_cp1252_cli_and_translations_parity_20261009.py`)**:
  - 7 neue Unit- und Contract-Tests zur Absicherung der cp1252-Encoding-Sicherheit, des `_emit_cli_report`-Fallbacks, der 6-Sprachen-Paritätsprüfung via `manage_translations --check` und End-to-End CLI-Ausführung unter `PYTHONIOENCODING=cp1252` (7/7 passed, Gesamtsuite 264 passed, 3 skipped).

### Discoverability, Visuelle Vier-Sichten-Topologie & Design (Pfad B 2026-10-08)
- **Visuelle Vier-Sichten-Architektur (Four-View ASCII Topology)**: Bereitstellung der vollständigen ASCII Four-View Architectural Topology in Abschnitt 2 von `README.md` und `README_de.md` (`VIEW 1..4` / `SICHT 1..4`) mit Projektion aller 10 Invarianten `INV-LOCAL-01` bis `INV-SLA-10` über Desktop-GUI/CLI/PWA, inerte AST-Analyse- & Duplikat-Engine, reversiblen Auto-Fix & atomare Publikation sowie RunAsInvoker Zero-Egress Sicherheitsperimeter.
- **18-Punkte Bilinguale Schnellnavigation**: Vollständige bilaterale Harmonisierung von `README.md` und `README_de.md` mit reziproken dualen HTML-Ankern (`<a id="sec-01"></a>` bis `<a id="sec-18"></a>`) und Schnellnavigationsleiste über alle 18 nummerierten Abschnitte.
- **Zielgruppen & Discoverability (Personas & Search Queries)**: Definition von 4 Entwickler-Personas (`PERSONA-01` bis `PERSONA-04`) und 10 hochspezifischen Suchanfragen in deutscher und englischer Sprache in Abschnitt 3.
- **10-Dimensionen Vergleichsmatrix vs. Linters**: Detaillierte architektonische Gegenüberstellung gegenüber `pylint`, `flake8`, `vulture` und `radon` über 10 technische Dimensionen und Laufzeitinvarianten in Abschnitt 9.
- **Level 1 SBOM Text-Begleiter Re-Audit Stand 2026-10-08**: Re-Auditierung von `THIRD_PARTY_LICENSES.txt` und `THIRD_PARTY_LICENSES.md` Stand 2026-10-08 mit Invarianten-Kreuztabelle, unprivilegierter `RunAsInvoker`-Zertifizierung, § 521 BGB Gefälligkeitsrecht und verbindlicher 48h-Sicherheits-SLA.
- **PEP 621 Metadaten-Erweiterung**: `pyproject.toml` um `Third-Party-Licenses (Text)`, `LLM-Ready` und `Contributing` URLs ergänzt unter strikter Wahrung des Versions-Freezes auf Version `3.0.2` (per `T-20260920-167562623`).
- **Bilinguale Beitragsrichtlinie (`CONTRIBUTING.md`)**: Umfassender Ausbau mit Spezifikation aller 10 Invarianten, Plan-D-Workflow (`C:\_Local_DEV\repos\MethodenAnalyser`), Pre-Commit-Toren und gesetzlichem Haftungsausschluss.
- **Vertragstest-Erweiterung (`tests/test_metadata.py`)**: 6 neue automatisierte Tests für Vier-Sichten-Topologie, 18-Punkte-Navigation, Personas, Level 1 SBOM und Pfad-B-Recency Stand 2026-10-08.

### UX, Barrierefreiheit & Tastatur-Ergonomie (UX & Accessibility Review 2026-10-03)
- **Barrierefreie Menüleiste mit Mnemonics**: Vollständige Menüleiste (`&Datei`, `&Aktionen`, `&Sprache`, `&Hilfe`) nach WCAG 2.1 AA / BITV 2.0 mit Mnemonics und Standard-Shortcuts (`Alt+D`/`Ctrl+O` Datei analysieren, `Alt+P`/`Ctrl+Shift+O` Projekt analysieren, `Ctrl+S` Bericht speichern unter..., `Ctrl+Q` Beenden, `Alt+F` Auto-Fix, `Ctrl+A` Alles auswählen, `Ctrl+C` Kopieren, `Ctrl+L` Ausgabe leeren, `F1` Tastaturkürzel & Barrierefreiheit, `Shift+F1` Über MethodenAnalyser).
- **Zentraler Dialog für Tastaturkürzel & Barrierefreiheit (`show_shortcuts_dialog`)**: Neuer modaler, strukturierter Dialog mit kategorisierter Tastaturbefehls-Übersicht (Navigation & Analyse, Bearbeiten & Aktionen, Hilfe & Steuerung), Schließen per `Escape`/`Return` und offiziellem Barrierefreiheits-Konformitätshinweis nach WCAG 2.1 AA und BITV 2.0; abgesichert mit Headless-Offscreen-Bypass.
- **Ausgabefeld-Ergonomie & Kontextmenü**: Vollwertiges Rechtsklick- und Tastatur-Kontextmenü (`<Button-3>`, `<App>`) auf dem Ausgabefeld (`ScrolledText`) mit Schnellaktionen für Kopieren, Alles auswählen, Bericht speichern und Ausgabe leeren; native Tastaturbindung für `Ctrl+A`/`Ctrl+a` (Alles auswählen).
- **Berichtsexport & Ansichtsverwaltung**: Neue Exportfunktion `save_report_as` zum gezielten Speichern von Analyseberichten mit Dateiauswahldialog sowie `clear_output_view` zur schnellen Bereinigung der Ausgabefläche und Wiederherstellung des Willkommenstextes mit Statusleisten-Feedback.
- **Tier-2 6-Sprachen-Parität (P-006)**: 24 neue Lokalisierungsschlüssel für Menüs, Dialoge, Tastaturbefehle und Barrierefreiheitshinweise in `locales/translations.json` mit 100% Parität über Deutsch, Englisch, Spanisch, Chinesisch, Japanisch und Russisch (183 Keys gesamt) und strikter Einhaltung echter deutscher Umlaute.
- **Vertragstest-Suite (`tests/test_ui_accessibility.py`)**: 6 neue automatisierte Tests für Shortcuts-Dialog Lifecycle & A11y, Headless-Bypass, mehrsprachige Generierung, Ausgabefeld-Leeren, Menüleisten-Shortcuts und vollständige Katalogparität (10/10 Tests passed, Gesamttestsuite auf 251 Tests ausgebaut, 100% grün).

### Sicherheit & Lizenz-Compliance (Security & License Audit 2026-10-02)
- **Dependency-Floors & Schwachstellen-Härtung**: `pytest` Mindestversion in `requirements-dev.txt` und `pyproject.toml` auf `>=9.1.1` gehärtet (Schutz vor CVE-2025-7117 / GHSA-6w46-j5rx-g56g); `ruff>=0.9.0`, `altgraph>=0.17.4`, `packaging>=24.0` und `pyinstaller>=6.10.0` als reproduzierbare Toolchain-Floors verankert.
- **PEP 621 Metadaten & Support-Kontakt**: `pyproject.toml` um `[project.optional-dependencies]` für `dev` und `build` erweitert; Maintainer-Support-E-Mail (`support@lukasgeiger.com`) und direkte GitHub Advisory Melde-URL (`https://github.com/dev-bricks/MethodenAnalyser/security/advisories/new`) unter `[project.urls]` hinterlegt.
- **Standardisiertes 5-Felder-SBOM-Inventar (`THIRD_PARTY_LICENSES.txt`)**: Vollständiges Lizenz-Inventar nach 5-Felder-Schema (`Package:`, `License:`, `SPDX:`, `URL:`, `Notice:`) für 10 Toolchain- und Standardbibliothek-Komponenten erstellt; MIT-Kompatibilität, Bootloader-Exception und reine Standardbibliothek-Laufzeit formal verifiziert.
- **Repository- & Gitignore-Hygiene (`.gitignore`)**: Ergänzung robuster Ignorier-Muster für Secrets (`secrets.*`), Zertifikate (`*.crt`) und Test-Artefakte (`pytest_out.txt`, `pytest*.txt`).
- **Vertragstest-Suite (`tests/test_security_license_contract.py`)**: 8 neue automatisierte Sicherheits-, Lizenz- und Hygiene-Vertragstests implementiert (Dependency-Floors, SBOM-Vollständigkeit, Security-Policy mit SLAs, Gitignore-Regeln, Secret-/Pfad-Hygiene, Lizenz-Parität, Local-First Invarianten und AST-Sicherheit). Testsuite auf 246 Tests ausgebaut (100% grün).

### Behoben
- **AST-Analyse & False-Positive-Beseitigung (`unused_defs`)**: Dunder/Magic-Methoden (`__init__`, `__str__`, `__enter__`, etc.), Callback-Referenzen (`ast.Load` in Datenstrukturen oder Funktionsargumenten), Klassen-/Typ-Verwendungen in Annotationen (`typehints`), öffentliche Modul-Exporte (`__all__`) sowie öffentliche Methoden exportierter Klassen werden nun verlässlich als genutzt erkannt (`filter_unused_defs`). Beseitigt False Positives in `unused_defs`, verhindert unberechtigte `EXIT_FINDINGS`-Fehlercodes (Exit 2) auf sauberem Code und korrigiert unberechtigte Punktabzüge im Projektreport (Bugsweep 2026-09-22).
- **AST-Analyse & Scope-Erkennung (`MethodenAnalyser3.py`)**: PEP 236 `from __future__ import <feature>` Compiler-Direktiven (z. B. `annotations`, `division`) werden nicht mehr als ungenutzte Runtime-Importe (`unused_imports`) oder ungenutzte globale Definitionen (`unused_global`) fehlgemeldet; `_file_has_findings` und CLI-Exit-Code bleiben bei sauberen Dateien mit Future-Imports verlässlich auf 0 (Bugsweep 2026-09-18).
- **AST-Analyse & PEP 695 TypeAlias (`MethodenAnalyser3.py`)**: `visit_TypeAlias` registriert `type Name = ...` und generische Typ-Aliase `type Box[T] = ...` als Definitionen in `defs` und `local_names`. Verhindert falsche `missing_defs`-Meldungen bei Aufruf und trackt unreferenzierte Typ-Aliase sauber in `unused_defs`.

### Optimiert
- **Performance & Verzeichnis-Pruning (`collect_python_files`)**: Umstellung von unselektivem `rglob("*.py")` auf `os.walk` mit top-down in-place Directory-Pruning (`dirs[:] = [...]`). Verhindert unnötigen Plattenzugriff in ausgeschlossene Verzeichnisbäume (`.git`, `.venv`, `node_modules`, `build`, `dist`).
- **Performance & I/O-Redundanz-Beseitigung (`analyze_project`)**: `AnalysisResult` zählt Zeilen (`total_lines`) direkt bei der AST-Analyse (`analyze_source`), wodurch der redundante zweite Datei-Lese-Durchlauf in `analyze_project` vollständig entfällt.

### Erweitert
- **PWA & Mobile-Icon-Inventar (`mobile_icons/`, `webapp/`)**: Vollständige Suite von Multi-Resolution-Icons (`icon-192.png`, `icon-512.png`, `apple-touch-icon-180.png`, `favicon.ico`, `manifest.json`, `manifest.webmanifest`) für Web Companion und native Mobile-Einbindung integriert.
- **Webapp-Server Root-Asset Fallback & MIME-Typen (`webapp/server.py`)**: Automatischer Fallback bei statischen Anfragen auf das übergeordnete `webapp/`-Verzeichnis für Standard-Browserpfade wie `/favicon.ico` und `/manifest.json`; `CONTENT_TYPES_BY_SUFFIX` um `.ico` (`image/x-icon`) und `.svg` (`image/svg+xml`) erweitert.
- **Asset- & Icon-Vertragstests (`tests/test_app_assets.py`, `tests/test_webapp_server.py`)**: 7 neue automatisierte Tests zur Validierung von Master-Icon, Store-Tile-Logos, Mobile-Icons-Suite, PWA-Manifesten sowie Root-Favicon- und Manifest-Serverendpunkten (Gesamttestsuite auf 238 Tests ausgebaut, 100% grün).
- **Desktop-UI Lokalisierung (`MA-I18N-02`)**: 25 neue Übersetzungsschlüssel in `locales/translations.json` über alle 6 Sprachen (`de`, `en`, `es`, `zh`, `ja`, `ru`), inklusive vollständiger Lokalisierung von Dateidialogen, Statusmeldungen, Export-Benachrichtigungen und Auto-Fix-Bestätigungen in `MethodenAnalyser3.py`.

## [3.0.2] - 2026-09-11

### Repository-Hygiene, CI-Matrix-Härtung & Vertragstest-Ausbau (Pfad A)
- **Versionsharmonisierung (v3.0.2)**: Paritätischer Versions-Bump auf `3.0.2` über alle Projekt-Artefakte hinweg (`MethodenAnalyser3.py`, `pyproject.toml`, `store_package.json`, `llms.txt`, `README.md`, `README_de.md` und `CHANGELOG.md`).
- **CI-Matrix & Test-Härtung (`.github/workflows/tests.yml` & `pyproject.toml`)**: Standardisierung des Testaufrufs auf `pytest -ra -v` sowohl in der CI-Matrix als auch in `[tool.pytest.ini_options].addopts` für detaillierte Zusammenfassungen bestandener und übersprungener Tests.
- **Lock- & Sync-Schutzhärtung (`.gitignore`)**: Ergänzung robuster Ignorier-Muster gegen Multi-Agenten-Locks (`uv.lock`), Cloud-Sync-Konfliktdateien (`*-WORKSTATION*`, `* (kopie)*`, `* (copy)*`) sowie Coverage- und Wheelhouse-Caches (`.coverage.*`, `coverage/`, `.wheel-smoke/`, `wheelhouse/`, `.tox/`).
- **PEP 621 Standard-Metadaten & URL-Aliase (`pyproject.toml`)**: Ergänzung von `Parent Organization` und `Umbrella Ecosystem` in `[project.urls]` zur standardisierten Ökosystem-Vernetzung mit `dev-bricks` und `open-bricks`.
- **Vertragstest-Erweiterung (`tests/test_metadata.py`)**: 4 neue automatisierte Vertragstests zur kontinuierlichen Verifikation von Test-Flags, Versionsparität, erweitertem `.gitignore`-Schutz und Marketing-Audit-Logs.
- **Index- und Badges-Aktualisierung (`llms.txt`, `README.md`, `README_de.md`)**: RAG-Index auf Version 3.0.2 und Prüfzeitstempel 2026-09-11 synchronisiert; Test- und Versions-Badges auf den aktuellen Stand aktualisiert.

## [3.0.1] - 2026-09-09

### Discoverability, Schnellnavigation & Governance-Härtung (Pfad B)
- **14-Punkte-Schnellnavigation (`README.md` & `README_de.md`)**: Vollständig paritätische Schnellnavigation mit funktionierenden Ankern für Features, Werkzeugvergleich, Architektur, Lebenszyklus, Governance-Invarianten, Bildschirmfoto, Installation, Bedienung, Web-Begleiter, Exit-Codes, Datenschutz, Sicherheitsrichtlinie, Partner-Ökosystem und Entwicklung/Tests.
- **Duale Mermaid-Diagramme**: Zweisprachige Systemarchitektur (`flowchart TD`) und detailliertes End-to-End Analyse-Sequenzdiagramm (`sequenceDiagram` mit `autonumber`) zur Visualisierung des AST-Parsings, Scope-Bindings, difflib-Duplikatsuche, JSON-Export und atomaren `.bak`-Backups bei Auto-Fix.
- **10 Governance- und Laufzeit-Invarianten**: Verbindliche Tabelle der Invarianten INV-LOCAL-01 bis INV-SLA-10 (Local-First, RunAsInvoker, inerte statische Analyse, Latin-1 Fallback, Loopback-Isolation, ZIP-Safety, atomarer Auto-Fix, Cross-Platform-Parität, Lock-Resilienz und 48h SLA).
- **Erweitertes Partner-Ökosystem**: 16 Partner-Repositories über `dev-bricks`, `ellmos-ai`, `file-bricks`, `doc-bricks` und `open-bricks` referenziert und verlinkt.
- **Sicherheitsrichtlinie & SLA-Härtung (`SECURITY.md`)**: 48h Erstbestätigungs-SLA, 5-Werktage-Triage-Zusage, koordinierte Offenlegung sowie offizielle Sicherheitskontakte (`security@open-bricks.org`, `security@ellmos.ai`, `support@lukasgeiger.com`, `lukas@open-bricks.org`) verankert.
- **CI-Matrix-Härtung (`.github/workflows/tests.yml`)**: Zusätzliches Bytecode-Validierungsgate (`python -m compileall -q .`) über das gesamte Repository integriert.
- **Multi-Agent Lock- & Sync-Schutz (`.gitignore`)**: Standard-Ignorierregeln für Multi-Agent-Locks (`LOCK*`, `*.lock`, `LOCK.permissions.json`) sowie Cloud-Sync-Konfliktdateien (`*-conflict-*`, `*-WORKSTATION-LG*`, `*-ASUS-GEI*`) gehärtet.
- **Drittanbieter-Transparenz (`THIRD_PARTY_LICENSES.md`)**: Umfassendes Dokument zur Null-Abhängigkeiten-Architektur (100% Python-Standardbibliothek) und abgegrenzten Entwickler-Toolchain (pytest, ruff, pyinstaller) erstellt.
- **Lokales Marketing-Register (`MARKETING-LOG.txt`)**: Lokales Logbuch mit Wertversprechen, Zielgruppen-Segmentierung, Discoverability-Suchbegriffen und Invarianten angelegt.
- **PEP 621 Metadaten (`pyproject.toml`)**: Version auf `3.0.1` angehoben; `Parent-Organization`, `Marketing-Log` und `Third-Party-Licenses` in `[project.urls]` ergänzt.
- **Index-Aktualisierung (`llms.txt`)**: Version 3.0.1, Governance-Invarianten und Zeitstempel auf 2026-09-09 synchronisiert.
- **Erweiterte Vertragstest-Suite (`tests/test_metadata.py`)**: 7 neue automatisierte Vertragstests für Schnellnavigation, duale Mermaid-Diagramme, Invarianten-Matrix, Partner-Ökosystem, .gitignore-Regeln, Drittanbieter-Deklaration und Marketing-Log (Gesamttestsuite auf 144 Tests / 15 Subtests ausgebaut, 100% grün).


- **Locale-Erkennung (`translator.py`)**: `detect_system_language()` erkennt System-Locale über Umgebungsvariablen (`LC_ALL`, `LC_MESSAGES`, `LANG`) und `locale.getlocale()`; `detect_language_from_header()` wertet HTTP `Accept-Language`-Header mit Qualitätsfaktoren (`q=...`) aus; `normalize_language_code()` normalisiert Sprachcodes auf die 6 unterstützten Sprachen (`de`, `en`, `es`, `zh`, `ja`, `ru`).
- **Übersetzungskatalog-Parität (`locales/translations.json`)**: 51 neue Lokalisierungsschlüssel für CLI-Sektionen, Statistiken, Tabellenüberschriften sowie Webapp-Status und Finding-Kategorien ergänzt (Gesamtkatalog auf 134 Keys mit 100% Parität über alle 6 Sprachen angehoben).
- **CLI-Lokalisierung (`MethodenAnalyser3.py`)**: CLI-Hilfe (`--lang`), Textreports und Projektberichte (`generate_report()`, `generate_project_report()`) dynamisch lokalisiert; Standardwert fällt transparent auf System-Locale zurück.
- **Webapp-Server & Endpunkte (`webapp/server.py`)**: `/api/translations` wertet `Accept-Language`-Header und Query-Parameter `?lang=` aus; `/api/analyze` erzeugt Textreports in der gewünschten Client-Sprache; `--lang` CLI-Parameter für Server-Start hinzugefügt.
- **Webapp-Frontend (`webapp/static/index.html`, `webapp/static/app.js`)**: Vollständige Lokalisierung aller UI-Labels, Finding-Kategorien, dynamischen Statusanzeigen und Details-Elemente über `data-i18n` und `t()`.
- **Testabdeckung & Regressionstests**: Neue Tests in `tests/test_cli.py` (`CliLocalizationTests`) und `tests/test_webapp_server.py` ergänzt (Gesamttestsuite auf 131 Tests / 15 Subtests ausgebaut, 100% grün).

### Repository-Hygiene & CI-Matrix-Härtung (Pfad A) [2026-09-07]
- **CI-Matrix-Härtung (`.github/workflows/tests.yml`)**: Concurrency-Steuerung (`cancel-in-progress`) integriert, Matrix um Python 3.13 erweitert, automatisierte Testausführung via `pytest -v` und Ruff Linting standardisiert.
- **PEP 621 Standard-Metadaten (`pyproject.toml`)**: Vollständige `[project.urls]` (Homepage, Documentation, Repository, Issues, Changelog, Security, Umbrella) deklariert, Python 3.13 sowie OS-Klassifikatoren (Linux, Windows, MacOS) ergänzt, CLI- und GUI-Entrypoints (`[project.scripts]`, `[project.gui-scripts]`) hinterlegt.
- **Zweisprachige Sicherheitsrichtlinie (`SECURITY.md`)**: Umfassende zweisprachige Richtlinie (English & Deutsch) mit klaren Garantien für Local-First, Zero-Egress, Schreibschutz bei Quelltextanalysen (Read-Only), Unprivileged User-Mode und inerte statische Analyse ohne dynamische Code-Ausführung; koordinierte Meldewege via GitHub Private Vulnerability Reporting und dedizierte Sicherheitskontaktadressen hinterlegt.
- **Vertragstest-Erweiterung (`tests/test_metadata.py`)**: 3 neue automatisierte Vertragstests für PEP 621 URLs/Metadaten, zweisprachige Sicherheitsrichtlinie und CI-Workflow-Integrität hinzugefügt (Gesamttestsuite auf 124 Tests / 15 Subtests erhöht, 100% grün).
- **Synchronisation von Dokumenten und Badges**: Test- und Python-Badges in `README.md` und `README_de.md` auf 124 Tests (Python 3.10 - 3.13) aktualisiert, `llms.txt` Zeitstempel auf 2026-09-07 synchronisiert.

### Internationalisierung [2026-08-27]
- **MA-I18N-05:** CLI erhält `--lang` für Hilfe und die zentralen Textreport-Zusammenfassungen. Der lokale Web-Hilfsmodus bietet eine sichtbare Sechs-Sprachen-Auswahl und lädt den flachen `web_*`-Katalog über den lokalen Endpunkt `GET /api/translations` aus der gemeinsamen `locales/translations.json`-Quelle. Keine Cloud-Abhängigkeit, keine neue Produktlinie.
- **Regressionen:** CLI-Sprachwahl, gemeinsamer Web-Katalog, HTTP-Endpunkt und die bestehende persistente Report-Wiederherstellung sind automatisiert abgesichert.

### Sicherheit [2026-08-25]
- **Inerte statische Analyse:** Modulnamen aus analysiertem Quelltext werden nicht mehr dynamisch importiert. Attributprüfungen verwenden ausschließlich statische Exporttabellen oder bereits geladene Module; ein Regressionstest belegt, dass Import-Nebeneffekte aus Eingabecode nicht ausgeführt werden.

### Internationalisierung & AST-Erweiterungen (MA-I18N-01 bis MA-I18N-04) [2026-08-25]
- **Multi-Language-Engine gem. P-006 (`translator.py`)**: `TranslationSystem` auf 6 Sprachen (`de`, `en`, `es`, `zh`, `ja`, `ru`) mit mehrstufiger robuster Fallback-Kette (`Zielsprache -> en -> de -> Key`), Pfadrobustheit und typisierter Schnittstelle (`get_supported_languages()`, `is_supported_language()`) angehoben.
- **Vollständiger 6-Sprachen-Katalog (`locales/translations.json`)**: Sämtliche Dialog-, Aktions-, Tooltip-, Menü- und Statusmeldungen für Deutsch, Englisch, Spanisch, Chinesisch, Japanisch und Russisch übersetzt.
- **GUI-Sprachmenü & Live-Umschaltung (`MethodenAnalyser3.py`)**: Menüleiste um direkte Sprachauswahl für alle 6 Sprachen erweitert; Live-Neuübersetzung von Fenstertitel, Aktionsschaltflächen, Tooltips, Statusleiste und Willkommensansicht ohne Neustart; persistiert in der Benutzerkonfiguration.
- **AST Pattern-Matching & Relative Imports (`MethodenAnalyser3.py`)**: Unterstützung für Python 3.10+ Pattern Matching (`MatchAs`, `MatchStar`, `MatchMapping`), `Global`/`Nonlocal` Deklarationen, relative Imports ohne Modulnamen (`from . import config, utils`) und Python 3.12+ `ast.TypeAlias`.
- **Automatisierte Testsuiten**: 8 neue Tests in `tests/test_i18n_translator.py` und `tests/test_ast_enhancements.py` sowie Aktualisierung von `test_language_switch.py`, `test_metadata.py` und `test_ui_accessibility.py` (Gesamttestsuite auf 113 Tests / 13 Subtests erhöht, 100% grün).

### Fehlerbehebungen / Bug Fixes (BS-20260821) [2026-08-21]
- **Import-Scope-Analyse & From-/Alias-/Relative-Import-Präzision (`MethodenAnalyser3.py`)**: `ImportScopeAnalyzer.visit_ImportFrom` erfasste bisher fälschlicherweise das Ursprungsmodul (`node.module.split(".")[0]`) anstelle der tatsächlich in den Scope gebundenen Bezeichner bzw. Aliase; zudem wurden relative Imports ohne Modulangabe (`from . import sibling`) ignoriert und aliased Imports (`import os.path as osp`) auf das Stamm-Modul reduziert. Dadurch kam es bei aktiv genutzten From-Imports (z. B. `from math import sqrt`) oder Alias-Imports zu falschen `unused_global`-Warnungen im Report. Fix: `visit_Import` und `visit_ImportFrom` binden die tatsächlichen Bezeichner/Aliase an den aktuellen Scope, und `_analyze_import_scopes` gleicht diese präzise gegen alle genutzten Namen inkl. String-Literale (`_string_refs`) ab. 5 neue Regressionstests in `tests/test_bugsweep_import_scopes_20260821.py` ergänzt (Gesamttestsuite: 105 Passed / 100% grün).

### UX & Barrierefreiheit / Accessibility (UX-003) [2026-08-21]
- **Barrierefreie Tooltips (`ToolTip`)**: Leichtgewichtiges, barrierefreies Tooltip-Widget für Tkinter implementiert. Unterstützt Maus-Hover (`<Enter>`/`<Leave>`), Tastaturfokus (`<FocusIn>`/`<FocusOut>`) und dynamische Aktualisierung bei Sprachwechsel für alle Hauptaktionsschaltflächen (`btn_analyze_file`, `btn_info`, `btn_autofix`, `btn_analyze_project`).
- **Live-Statusleiste (`status_bar`)**: Barrierefreie Statusleiste am unteren Fensterrand integriert, die Kontext- und Tastaturhinweise beim Fokussieren/Hovern sowie den Echtzeit-Fortschritt bei Dateianalyse, Projektanalyse und Auto-Fix zurückmeldet.
- **Vollständige Live-Neuübersetzung**: Beim Umschalten der Sprache („Sprache / Language") werden Fenstertitel, Schaltflächen, Tooltips, Menüleisten-Einträge und Statusleisten-Texte dynamisch und verlustfrei aktualisiert.
- **Lokalisierungskatalog & Typografie**: `locales/translations.json` um 18 neue Schlüssel (Statusmeldungen, Dialogtitel, Aktionshinweise) für Deutsch und Englisch mit strikter Einhaltung echter deutscher Umlaute (`ä`, `ö`, `ü`, `ß`) erweitert.
- **Automatisierte Testsuite**: 4 neue Tests in `tests/test_ui_accessibility.py` sichern Tooltip-Lebenszyklus, Katalogvollständigkeit, echte deutsche Umlaute und dynamische Neuübersetzung ab (Gesamttestsuite auf 100 Passed / 100% grün).

## [3.0.0] - 2026-08-16

### Discoverability, README-Design & Toolchain-Harmonisierung (Pfad B)
- **Badges & Discoverability**: Pytest-Status-Badge (96 Passed) sowie Version (3.0.0) in `README.md` und `README_de.md` integriert.
- **Interaktive Systemarchitektur**: Zweisprachige Mermaid Systemarchitektur- und Datenflussdiagramme (Eingabe, AST-Analyse-Engine, Export/GUI/CLI/Web) ergänzt.
- **Ökosystem-Cross-Referencing**: Übersicht der verwandten Werkzeuge innerhalb der `dev-bricks`- und `open-bricks`-Ökosysteme (`DevCenter`, `CodeBox`, `CareCenter-for-Codex`, `lock-master`) dokumentiert.
- **Packaging & Toolchain-Standardisierung**: `pyproject.toml` mit standardisierter Build-Konfiguration, `[tool.pytest.ini_options]` und `[tool.ruff]` (py310, line-length 120) angelegt.
- **Metadaten- & Manifest-Testsuite**: Automatisierte Testsuite in `tests/test_metadata.py` zur Validierung von Versionsparität (`MethodenAnalyser3.py`, `pyproject.toml`, `store_package.json`, `CHANGELOG.md`), Dokumentenintegrität, Übersetzungsstruktur (`locales/translations.json`) und Exportformat-Konstanten erstellt.
- **`llms.txt`**: Last-checked Zeitstempel auf `2026-08-16` und Teststand auf 96 Tests synchronisiert.

### Vertrags-Synchronisation [2026-08-11]
- `EXPORTFORMAT.md`, `WEBAPP.md` und beide READMEs unterscheiden jetzt
  API-Eingänge (`snippet`, `file`, `zip`) von importierten `project`-Reports;
  `project`-POSTs werden durch den lokalen Server abgelehnt.
- `requirements-dev.txt`, `BUILD.md` und `_sources/CROSSCHECK.md` definieren
  den getrennten, getesteten pytest-/PyInstaller-Bereich. Die Runtime bleibt
  Standardbibliothek-only.
- README-Git-Hygiene beschreibt nun einen benannten Branch-/Commit-Check statt
  einer dauerhaft behaupteten Ahead/Behind-Snapshot-Zahl.

### Repository-Hygiene [2026-08-07]
- **Pfad A Maintenance**: Badges in `README.md` & `README_de.md` um `dev-bricks` Ecosystem-, `open-bricks` Umbrella- und LLM-Ready-Badges erweitert.
- GFM Callout-Box für `llms.txt` RAG-Index in `README.md` und `README_de.md` eingebunden.
- `llms.txt` Last-checked Zeitstempel auf `2026-08-07` und Pytest-Teststand (`82 passed`) synchronisiert.

### Neue Funktionen / Features
- **UX-002 / Welle-1 U1** (`MethodenAnalyser3.py`, `locales/translations.json`): Sichtbarer Sprachschalter in der Menüleiste („Sprache / Language" → „Deutsch" / „English"). Menü, Schaltflächen, Tastaturhinweis und Willkommenstext stellen sich sofort um; die Auswahl wird pro Benutzer in `%APPDATA%\MethodenAnalyser\config.json` (bzw. `~/.config/MethodenAnalyser/config.json`) persistiert und beim nächsten Start wiederhergestellt. Das bisher ungenutzte `translator.py` / `locales/translations.json` ist damit im UI erreichbar. Regressionstests in `tests/test_language_switch.py`.

### Build / Packaging
- **Dev-Toolchain & PyInstaller-Fix** (`requirements-dev.txt`, `build_exe.bat`): `requirements-dev.txt` zur reproduzierbaren Definition der Entwicklungswerkzeuge (`pytest>=8.0.0`, `pyinstaller>=6.0.0`) angelegt; `build_exe.bat` schlägt bei fehlendem optionalen Build-Exclude-Scanner nicht mehr fehl, sondern baut sauber ohne Scanner-Excludes weiter.
- `releases/v3.0.0/PROVENANCE.md` dokumentiert den tatsächlichen lokalen Artefaktstand. Das historische v3.0.0-Bundle ist wegen fehlender Commitkette und einer vom gespeicherten Wert abweichenden EXE-SHA-256 bis zu einem reproduzierbaren Neubuild gesperrt; es wurde weder gelöscht noch durch eine neue Version ersetzt.
- `build_exe.bat` ergänzt einen reproduzierbaren PyInstaller-Build mit lokalem Workpath (lokales Build-Verzeichnis), zentralem Build-Exclude-Scanner und Kopie der fertigen EXE nach `dist\MethodenAnalyser.exe` sowie `MethodenAnalyser.exe`.
- `START.bat` startet unter Windows bevorzugt die gebaute EXE und fällt erst danach auf den Python-Start zurück.
- `MethodenAnalyser.spec` nutzt relative Projektpfade, bündelt Icon und `locales/` und deaktiviert UPX.
- GitHub-Actions-Smoke-Matrix pinnt Windows auf `windows-2025-vs2026` und macOS auf `macos-26`, damit die 2026-Runner-Migration vor dem Stichtag validiert wird.

### Fehlerbehebungen / Bug Fixes
- **BS-20260814** (`MethodenAnalyser3.py`): Modul-Attribut-Aufrufe mit verschachtelten Attributketten (wie z. B. `concurrent.futures.ThreadPoolExecutor`, `urllib.request.build_opener`) oder neuere Standard-Library-Methoden (`asyncio.to_thread`) wurden fälschlich als fehlende Definitionen (`missing_defs`) gemeldet, weil `CodeAnalyzer` nur einstufige Attributzugriffe erfasste und `get_available_module_attributes` auf eine unvollständige statische Tabelle beschränkt war. Fix: `_extract_attribute_chain()` für mehrstufige AST-Attributketten, dynamische Reflection mit `importlib`/`dir()` und Caching via `@lru_cache`, sowie rekursive Type-Hint-Extraktion (`_extract_typehints`) für verschachtelte Annotationen (`List[...]`, `Optional[...]`). 6 Regressionstests in `tests/test_bugsweep_ast_attribute_typehints_20260814.py` ergänzt.
- `webapp/server.py`: Statische Dateien werden nur noch über strikt normalisierte Pfade unterhalb der erlaubten Roots ausgeliefert; Content-Types kommen aus einer festen Endungs-Whitelist statt aus frei abgeleiteten Pfadwerten.
- **A11Y-002** (`webapp/static/index.html`, `webapp/static/app.js`): Die Quelltyp-Umschaltung im Web Companion (`Snippet`, `Datei`, `ZIP`) markiert den aktiven Modus jetzt zusätzlich mit `aria-pressed`; Screenreader können den Segmentzustand damit erkennen, ohne dass die kompakte Oberfläche sichtbare Zusatzbeschriftungen braucht. Regressionstest in `tests/test_webapp_server.py`.
- **BS27-1** (`MethodenAnalyser3.py`): `run_project_analysis()` rief `output_widget.update()` auf (Zeilen 1529 + 1534), wodurch User-Events (z. B. Button-Klicks) während der laufenden Projektanalyse verarbeitet wurden — re-entranter Aufruf der Funktion war möglich. Fix: beide Aufrufe auf `update_idletasks()` geändert (verarbeitet nur Render-/Layout-Jobs, keine User-Events). Regressionstests in `tests/test_bugsweep_gui_threading_export_20260627.py`.
- **BS27-2** (`MethodenAnalyser3.py`): `analyze_project()` ignorierte `UnicodeDecodeError` in der `total_lines`-Zählschleife kommentarlos (kein Latin-1-Fallback) — Zeilenzahl für Latin-1-kodierte `.py`-Dateien wurde als 0 gezählt. Fix: Latin-1-Fallback konsistent mit `analyze_file()` ergänzt. Regressionstest in `tests/test_bugsweep_gui_threading_export_20260627.py`.
- **BS27-3** (`MethodenAnalyser3.py`): `run_analysis()` verwendete das Emoji `📄` im Widget-Insert für den Datei-Header (Zeile 1095) — inkonsistent mit dem vorherigen Emoji-Cleanup in `get_summary()`. Fix: `📄` durch `[DATEI]` ersetzt.
- **UX-001** (`MethodenAnalyser3.py`): Die Hauptaktionen der Tkinter-GUI hatten keine sichtbaren Tastaturhinweise und keine direkten Shortcuts. Fix: kompakte Shortcut-Zeile (`Alt+D`, `Alt+P`, `Alt+F`, `F1`) ergänzt, globale Tastaturkürzel gebunden und die Initialansicht auf Tastaturnutzung vorbereitet. Regressionstests in `tests/test_cli.py` sichern Hinweistext und Shortcut-Bindings ab.
- **B-004** (`MethodenAnalyser3.py`): `auto_fix_unused_imports` las Dateien ausschließlich als UTF-8, was bei Latin-1-kodierten Quellcode-Dateien zu `UnicodeDecodeError` führte. Fix: UTF-8-First mit `latin-1`-Fallback via `readlines()` (Zeilennummern bleiben mit `ast.lineno` synchron). 9 Regressionstests in `tests/test_cli.py` ergänzt.
- **B-005** (`MethodenAnalyser3.py`): `analyze_project` fing nur `IOError`/`OSError`, nicht `UnicodeDecodeError` — Latin-1-Dateien brachen den gesamten Projekt-Scan ab. Fix: `UnicodeDecodeError` in denselben `except`-Block aufgenommen.
- **B-006** (`MethodenAnalyser3.py`): Backup- und Output-Schreibvorgänge nutzten immer UTF-8, was Latin-1-Dateien mit Non-ASCII-Zeichen korrumpierte. Fix: erkannte Encoding-Information wird beim Schreiben wiederverwendet.
- **B-007** (`MethodenAnalyser3.py`): `_collect_unused_import_lines` entfernte `from __future__ import annotations` fälschlich als ungenutzt. Fix: `__future__`-Imports werden übersprungen (PEP-563-Semantik).
- **B-008** (`MethodenAnalyser3.py`): `CodeAnalyzer.visit_ExceptHandler` trug Binding-Namen aus `except ... as e`-Blöcken nicht in `local_names` ein — `ExceptHandler.name` ist ein `str`, kein `ast.Name`-Knoten und wurde von `visit_Name` nicht erfasst. Fix: explizite Eintragung in `local_names`.
- **B-009** (`MethodenAnalyser3.py`): `analyze_source` listete `__file__`, `__name__`, `__doc__` als fehlende Imports, weil Modul-Level-Dunders nicht in `builtins` enthalten sind. Fix: Dunders werden aus `missing_imports` herausgefiltert.
- **B-001** (`translator.py`): `_is_german()` erkannte englische Wörter fälschlich als Deutsch, weil die Zeichenmenge `"aeoeueAeOeUess"` als einzelne ASCII-Zeichen iteriert wurde statt als echte Umlaute. Fix: Prüfung auf `"äöüÄÖÜß"` (Unicode). Regressionstest in `tests/test_cli.py` ergänzt.
- **B-002** (`MethodenAnalyser3.py`): `_collect_unused_import_lines()` markierte `import os.path` nicht zur Entfernung, weil `alias.name` den Wert `"os.path"` liefert, während `unused_set` nur `"os"` enthält. Fix: `alias.name.split(".")[0]`. Regressionstest ergänzt.
- **B-003** (`MethodenAnalyser3.py`): `scan_dynamic_usage()` gab Strings wie `"getattr("`, `"setattr("` als extrahierte Methodennamen zurück, weil Regex-Muster ohne Capture-Group den vollen Match liefern. Fix: Strings mit `(` werden ausgefiltert. Regressionstest ergänzt.

### Repository-Hygiene
- `README.md` überarbeitet und auf ein strukturiertes, englischsprachiges Layout (English-first) mit Tabellen, Badges und Verweisen umgestellt.
- Neue deutsche Übersetzung `README_de.md` für vollständige Lokalisierung erstellt.
- `llms.txt` aktualisiert und mit `README_de.md` ergänzt.
- Community-Workflows aktualisiert: `actions/stale@v10` und `actions/first-interaction@v3` mit aktuellen Input-Namen.

### Portierung / Platforms
- `PORTIERUNGSPLAN.md` ist nach User-Korrektur auf Desktop-only geschärft: Windows Store bleibt Hauptkanal, macOS/Linux bleiben Source-Smoke-Ziele, Web/PWA/Android/iOS sind keine Produktlinien.
- Die vorhandene lokale Weboberfläche wird nur noch als Hilfs-/Demo-Modus innerhalb des Desktop-Projekts geführt, nicht als Companion-App.
- README, WEBAPP.md und EXPORTFORMAT.md verwenden entsprechend keine Companion-Roadmap mehr.
- `AUFGABEN.txt` enthält konkrete P0-P3-Aufgaben für CLI-Modus, JSON-Export, PWA-Companion und Cross-Platform-Smoke-Tests.
- Windows-Store-P0 abgeschlossen: `_WARTUNG/generate_store_screenshots.py` erzeugt jetzt reproduzierbar `main.png`, `file-analysis.png`, `project-analysis.png`, `duplicate-detection.png` und `manifest.json` unter `releases/windowsstore/screenshots/`.
- `releases/windowsstore/store_settings.json`, `BUILD.md` und die DE/EN-Store-Listings sind auf den realen Projektstand, aktuelle GitHub-URLs und den dokumentierten Pretest-Workflow synchronisiert.

### Hinzugefügt / Added
- `tests/test_webapp_server.py` sichert jetzt die HTTP-Request-Grenze (413), ungültiges Base64, beschädigte und Python-lose ZIPs, Einzeldatei-/Gesamtgrößen, Dateianzahl sowie Windows-Backslash-Traversal ab.
- Die lokale Web-Runtime weist für den bewussten LAN-Testmodus auf lokales HTTP ohne Authentifizierung/TLS hin. WEBAPP, README-Paar, Portierungsplan und Privacy-Policy halten den Loopback-Standard, die vertrauenswürdige-LAN-Grenze und den Nicht-Ziel-Status der Mobile-Produktlinie konsistent fest.
- GitHub-Actions-Smoke-Matrix prüft den Quellstand jetzt auf Windows (Python 3.10-3.12) sowie zusätzlich auf Ubuntu und macOS (Python 3.11), inklusive Compile-, Tkinter-Import- und `unittest`-Smoke.
- Lokaler Web/PWA-Companion unter `webapp/` mit Snippet-/Einzeldatei-Analyse über den bestehenden Python-Analyse-Kern.
- Web/PWA-Companion kann jetzt auch kleine ZIP-Archive mit `.py`-Dateien lokal hochladen, temporär entpacken und als Mini-Projekt analysieren.
- Web/PWA-Companion speichert Entwürfe und den letzten JSON-Report jetzt lokal im Browser.
- Web/PWA-Companion kann jetzt bestehende `methodenanalyser-report-v1.json`-Dateien importieren und lokal wieder anzeigen.
- Web/PWA-Companion zeigt jetzt einen eigenen Android/iOS-Testpfad mit LAN-Startkommando, Laufzeitmetadaten, erkannten WLAN-URLs und getrennten Install-Hinweisen.
- Web/PWA-Companion zeigt jetzt zusätzlich eine kopierbare PWA-Testkarte mit Install-Flow, Service-Worker-, Speicher-, Viewport- und Server-Diagnose für Android-/iOS-Smokes.
- `START_WEBAPP.bat` startet den Web Companion unter Windows per Doppelklick.
- `WEBAPP.md` dokumentiert lokalen Start, API, Datenschutz und Grenzen der ersten PWA-Linie.
- `tests/test_webapp_server.py` deckt die API-Hülle für Snippet-, Datei- und ZIP-Payloads ab.
- CLI-Modus für Datei- und Projektanalyse via `--file` und `--project`, inklusive definierter Exit-Codes für Automationen.
- JSON-Export über `--json-output` im Schema `methodenanalyser-report-v1.json`, inklusive Datei-, Projekt- und stdin-Snippet-Analyse.
- `EXPORTFORMAT.md` dokumentiert Top-Level-Felder, `files[]`-Einträge und Stabilitätsregeln für Web/PWA-Companions.
- `tests/test_cli.py` deckt CLI-Erfolg, Findings, Teilfehler und Fehlerpfade per `unittest` ab.
- `tests/test_store_screenshots.py` deckt den Screenshot-Manifest-Pfad für die Store-Artefakte ab.
- README dokumentiert jetzt den GitHub-/Privacy-Hygiene-Check vom 2026-05-16, den synchronen Branch-Stand und die lokalen Artefaktgrenzen.
- README bindet jetzt den vorhandenen GUI-Screenshot aus `README/screenshots/main.png` direkt ein.
- Das Hauptfenster verwendet das lokale `MethodenAnalyser.ico`, wenn es verfügbar ist.
- GitHub Actions Smoke-Test kompiliert die Python-Dateien auf Python 3.10 bis 3.12.
- `RELEASES.md` dokumentiert die lokale Release-Struktur ohne Build-Artefakte ins Repository aufzunehmen.

### Geändert / Changed
- `.gitignore` schließt zusätzliche Cache-, Coverage- und Signierartefakte aus.
- `STORE_LISTING.md` verwendet im deutschen Store-Text echte Umlaute statt Umschreibungen.
- README, SECURITY und CONTRIBUTING verweisen auf `dev-bricks/MethodenAnalyser`.
- `START.bat` setzt UTF-8/PYTHONIOENCODING und nutzt `py -3` mit `python`-Fallback.
- Lokale Release-Artefakte bleiben unter dem ignorierten `releases/`-Ordner oder in GitHub Releases.
- Projekt- und ZIP-Reports verwenden im JSON jetzt einen sprechenden Quellnamen statt eines temporären Arbeitsordners.
- Manifest, Install-Flow und Service Worker stützen jetzt installierbare/offline-fähige PWA-Nutzung.
- Die Companion-Oberfläche aktualisiert jetzt eine PWA-Testkarte live bei Install-Status-, Speicher- und Viewport-Änderungen.
- `tests/test_webapp_server.py` prüft jetzt zusätzlich Laufzeitmetadaten, Manifest, Service-Worker-Header und Offline-Seite über einen lokalen HTTP-Server.
- `tests/test_webapp_server.py` prüft jetzt auch die neuen PWA-Testkarten-Controls und den lokalen Runtime-Pfad.
- Web/PWA-Doku beschreibt den Report-Import jetzt explizit als Austauschpfad zwischen Desktop- und Companion-Linie.
- README beschreibt jetzt explizit den neuen macOS-/Linux-Source-Smoke-Pfad und grenzt ihn gegen eine echte Packaging-Linie ab.

### Behoben / Fixed
- Info-Dialog in `create_gui()` zeigte hardcodiert „Python Code Analyzer v2.0" statt des tatsächlichen `TOOL_VERSION`-Werts (3.0); Zeichenkette auf `f"Python Code Analyzer v{TOOL_VERSION}"` umgestellt, Copyright-Jahr auf 2026 aktualisiert.
- `do_POST()` in `webapp/server.py` gab bei ungültigem UTF-8-Request-Body HTTP 500 statt 400 zurück, weil `UnicodeDecodeError` nicht explizit abgefangen wurde; separater `except UnicodeDecodeError`-Handler ergänzt.
- `missing_imports` behandelt Modulattribute und lokale Parameternamen jetzt korrekt statt sie fälschlich als Importlücke zu melden.
- Die PWA lädt jetzt ohne unnötigen `favicon.ico`-404, weil App-Icon und Apple-Touch-Icon explizit eingebunden sind.
- Privacy-/Secret-Check ohne Befund; keine Credentials oder getrackten ignorierten Dateien gefunden.
- Öffentliche persönliche Kontakt-Mail aus `CODE_OF_CONDUCT.md` entfernt.
- Haftungshinweis ist jetzt auf die tatsächliche MIT-Lizenz beschränkt.

## [1.0.0] - YYYY-MM-DD

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release.
