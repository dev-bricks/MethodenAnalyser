# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

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
