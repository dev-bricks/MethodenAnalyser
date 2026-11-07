# Portierungsplan — MethodenAnalyser

Stand: 2026-11-07 (Tier-2 6-Sprachen-Harmonisierung & Store-Staging)

## Kurzentscheidung

MethodenAnalyser ist und bleibt vorrangig eine lokale Desktop-Anwendung für Windows (Standalone EXE und MSIX für den Windows Store), da der primäre Entwickler-Nutzen aus der direkten Dateisystem-Analyse lokaler Python-Projekte, der Duplikaterkennung und der sicheren automatischen Import-Bereinigung mit atomaren Backups entsteht.

Die plattformübergreifende Portierungsstrategie folgt der fundierten Nutzer-Entscheidung:
1. **Windows Desktop (Hauptlinie):** Vollständige Desktop-GUI (Tkinter), Headless-CLI (`--file`, `--project`), PyInstaller-EXE (`dist/MethodenAnalyser/MethodenAnalyser.exe`) und Windows Store MSIX (`releases/windowsstore/`).
2. **macOS und Linux (Source-Targets):** Volle Funktionsfähigkeit über Quellcode und CLI (`python MethodenAnalyser3.py --project <pfad>`), abgesichert durch automatisierten Source-Platform-Smoke (`tests/source_platform_smoke.py`). Keine separaten nativen Installer (.pkg/.deb) erforderlich.
3. **Web / Mobile (Nicht-Ziele):** Eine mobile App (Android/iOS) oder eine ausgelagerte Web/PWA-Cloud-Lösung ist für eine lokale Python-Code-Analyse weder sicherheits- noch usecase-adäquat (Nutzer-Entscheidung vom 2026-05-28 bestätigt). Die lokale Weboberfläche (`webapp/server.py`) dient rein als optionaler lokaler Hilfsmodus für isolierte Code-Snippets.

## Feature-zu-Usecase-Ableitung

| Feature der besten Version | Wann braucht man das? | Usecase |
|---|---|---|
| AST-basierte statische Codeanalyse | Bereinigung gewachsener Python-Codebasen, Vorbereitung von Refactorings | Entwickler-Arbeitsplatz |
| Sichere Import-Bereinigung (Auto-Fix) | Unbenutzte Imports mit atomarem Backup entfernen | Automatisierte Code-Hygiene |
| Duplikat- und Ähnlichkeitserkennung | Identifikation redundanter Logikblöcke für Abstraktion | Code-Review & Architektur-Audit |
| Headless-CLI & maschinenlesbarer Export | CI-Pipelines, Pre-Commit-Hooks und automatisierte Checks | Automations- und Batch-Workflows |
| Tier-2 6-Sprachen-Lokalisierung | Mehrsprachige Entwicklerteams in internationalen Projekten | Globaler Desktop-Einsatz |

## Statusmatrix

| Plattform | Zielstatus | Umsetzungsgrad / Verifikation |
|---|---|---|
| Windows Desktop (GUI/EXE) | Hauptlinie | Vollständig implementiert; PyInstaller-Buildvertrag (`build_exe.bat`), Tkinter-GUI, Single-Instance-Schutz |
| Windows Store (MSIX) | Produktiv | Gestagt in `releases/windowsstore/`; `AppxManifest.xml` mit 6 Sprachen, Store-Kacheln, 52+ Readiness-Checks PASS |
| macOS (Source / CLI) | Source-Target | Vollständig portabel; reines Python (stdlib `ast`), verifiziert via `tests/source_platform_smoke.py` |
| Linux (Source / CLI) | Source-Target | Vollständig portabel; POSIX-Pfade, CWD-Unabhängigkeit, verifiziert via `tests/source_platform_smoke.py` |
| Lokale Web-Hilfsansicht | Nebenfunktion | Vorhanden in `webapp/server.py` für lokales Snippet-Testing; kein Cloud-Einsatz |
| Android / iOS | Ausgeschlossen | Nicht-Ziel gemäß Nutzerentscheidung; keine mobile Code-Analyse-Linie |
