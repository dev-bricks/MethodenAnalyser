# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Portierung / Platforms
- `PORTIERUNGSPLAN.md` dokumentiert die Plattformstrategie: Windows Store zuerst, Web/PWA als gemeinsame Android-/iOS-/Web-Linie, macOS/Linux als Source-Smoke-Ziele.
- `AUFGABEN.txt` enthält konkrete P0-P3-Aufgaben für CLI-Modus, JSON-Export, PWA-Companion und Cross-Platform-Smoke-Tests.

### Hinzugefügt / Added
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
- `missing_imports` behandelt Modulattribute und lokale Parameternamen jetzt korrekt statt sie fälschlich als Importlücke zu melden.
- Die PWA lädt jetzt ohne unnötigen `favicon.ico`-404, weil App-Icon und Apple-Touch-Icon explizit eingebunden sind.
- Privacy-/Secret-Check ohne Befund; keine Credentials oder getrackten ignorierten Dateien gefunden.
- Öffentliche persönliche Kontakt-Mail aus `CODE_OF_CONDUCT.md` entfernt.
- Haftungshinweis ist jetzt auf die tatsächliche MIT-Lizenz beschränkt.

## [1.0.0] - YYYY-MM-DD

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release.
