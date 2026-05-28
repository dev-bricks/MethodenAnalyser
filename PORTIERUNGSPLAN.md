# Portierungsplan - MethodenAnalyser

Stand: 2026-05-27
Status: Windows-Store-P0 mit reproduzierbarem Screenshot-Satz, synchronisierten Store-Settings und dokumentiertem Dogfooding-Pretest abgeschlossen; CLI-, JSON-Export und lokaler Web/PWA-Companion inklusive ZIP-Upload, Report-Import, Install-Flow und Offline-Shell umgesetzt; Cross-Platform-Smoke-Automation für Windows/macOS/Linux eingerichtet

## Ausgangslage

MethodenAnalyser ist ein lokaler Python-Code-Analyser mit Tkinter-GUI und ohne externe Laufzeitabhängigkeiten. Der Kern nutzt Python-AST, Dateisystemzugriff und lokale Exporte. Dadurch ist die Desktop-Version technisch leicht auf Windows, macOS und Linux ausführbar, während mobile Plattformen wegen Dateizugriff, Projektordnern und Python-Laufzeit nicht sinnvoll als nativer Clone entwickelt werden sollten.

Die Nachfrage liegt vor allem bei Entwicklerinnen und Entwicklern, die kleine bis mittlere Python-Projekte vor Refaktorierungen, Code-Reviews oder Releases prüfen wollen. Mobilität ist sekundär: Auf Smartphone oder Tablet ist das Lesen ganzer Projektbäume unergonomisch, ein Web/PWA-Companion kann aber für einzelne Dateien, Snippets, Store-Demo und schnelle Checks nützlich sein.

## Zielbild

1. Windows bleibt der primäre Release-Kanal, inklusive Microsoft Store.
2. macOS und Linux bleiben schlanke Desktop-Zielplattformen über Source-Start und Smoke-Tests.
3. Web, Android und iOS werden als gemeinsame PWA-Linie behandelt, nicht als getrennte native Apps.
4. Die PWA analysiert zuerst einzelne Dateien, Snippets oder kleine ZIP-Uploads; große lokale Projektbäume bleiben Aufgabe der Desktop-App.
5. Desktop und PWA tauschen Ergebnisse über ein versioniertes JSON-Format aus.

## Plattformbewertung

| Plattform | Entscheidung | Begründung | Nächster Schritt |
|---|---|---|---|
| Windows Store | Priorität P0 | Beste Zielgruppe, vorhandene Store-Artefakte, keine externen Laufzeitabhängigkeiten | Screenshot-Satz, Listing und Dogfooding-Pretest sind fertig; als Nächstes MSIX-/WACK-Protokoll erneuern |
| Webapp / PWA | Priorität P1 | Gute Demo- und Companion-Linie für Snippets, einzelne Dateien und kleine Uploads | Install-/Offline-Verhalten lokal dogfooden und danach Android-/iOS-Browsertests durchführen |
| Android | P2 über PWA | Native App wäre Mehraufwand ohne klaren Mehrwert; PWA reicht für mobile Kurzchecks | Web Companion auf Android-Browser testen |
| iOS | P2 über PWA | Gleiche Logik wie Android; nativer App-Store-Weg lohnt aktuell nicht | Web Companion auf iOS Safari testen |
| macOS App | P3 | Tkinter/Python sollte laufen, aber Packaging und Signierung sind für die Zielgruppe nachrangig | Neue GitHub-Actions-Smokes für `macos-latest` beobachten; Packaging erst nach stabilen Läufen prüfen |
| Linux Version | P3 | Für Entwickler nützlich, aber Distribution über Source/ZIP reicht zunächst | Neue GitHub-Actions-Smokes für `ubuntu-latest` beobachten; Packaging erst nach stabilen Läufen prüfen |

## Architekturplan

### Desktop-Linie

- Bestehende Tkinter-App bleibt die Hauptversion.
- `analyze_file()`, `analyze_project()` und Report-Erzeugung bleiben die maßgebliche Kernlogik.
- Ergänzt werden sollte ein CLI-Modus, damit dieselbe Analyse ohne GUI für Tests, Automationen und spätere Web/PWA-Brücken nutzbar ist.
- Bestehender Textreport bleibt erhalten; zusätzlich wird ein JSON-Export eingeführt.

### Web/PWA-Linie

- Start als getrennte, kleine Companion-App, nicht als Umbau der Desktop-GUI.
- Erste Ausbaustufe umgesetzt: Code-Paste, einzelne `.py`-Dateien und kleine `.zip`-Archive laufen über einen lokalen stdlib-Python-Dienst unter `webapp/server.py`.
- Zweite Ausbaustufe umgesetzt: Install-Button, lokale Draft-/Report-Persistenz und Offline-Shell für bereits geladene PWA-Ressourcen.
- Dritte Ausbaustufe umgesetzt: Der Companion liefert jetzt einen eigenen Android/iOS-Testpfad mit LAN-Startkommando, Laufzeitmetadaten und getrennten Install-Hinweisen für Android sowie iPhone/iPad.
- Vierte Ausbaustufe umgesetzt: Eine PWA-Testkarte fasst Install-Flow, Service-Worker-Status, lokalen Speicher, Viewport und den aktiven Serverpfad als kopierbare Kurzdiagnose für mobile Smoke-Tests zusammen.
- Kein direkter Zugriff auf beliebige lokale Projektordner im Browser.
- Export/Import über `methodenanalyser-report-v1.json`, damit Desktop-Reports auch im Browser lokal geprüft werden können.
- Android und iOS nutzen dieselbe PWA statt eigener nativer Codebasen.

### Austauschformat

Vorgeschlagenes Format: `methodenanalyser-report-v1.json`

Mindestfelder:

- `schema_version`
- `tool_version`
- `source_kind` (`file`, `project`, `snippet`, `zip`)
- `generated_at`
- `files`
- `unused_imports`
- `unused_definitions`
- `missing_definitions`
- `duplicate_imports`
- `summary`

## Umsetzungsreihenfolge

1. P0: Windows-Store-Vorbereitung abschließen. (erledigt 2026-05-27)
2. P0: CLI-Modus für Datei- und Projektanalyse ergänzen. (erledigt 2026-05-24)
3. P1: JSON-Export `methodenanalyser-report-v1.json` aus Desktop-Kernlogik erzeugen. (erledigt 2026-05-24)
4. P1: PWA-Companion für Snippet-, Einzeldatei- und kleine ZIP-Analyse umsetzen. (erledigt 2026-05-24)
5. P1/P2: PWA-Installierbarkeit, Draft-Persistenz und Offline-Shell lokal absichern. (erledigt 2026-05-24)
6. P2: Android-/iOS-Browsertests für die PWA durchführen. Vorbereitung über LAN-Startpfad, Laufzeit-Hinweise und kopierbare PWA-Testkarte erledigt 2026-05-26.
7. P3: macOS- und Linux-Smoke-Tests für Source-Start automatisieren und dokumentieren. (CI-Vorbereitung erledigt 2026-05-26)

## Nicht-Ziele

- Kein nativer Android-Clone.
- Keine native iOS-App.
- Kein vollständiger Browser-Ersatz für lokale Projektordneranalyse.
- Keine Cloud-Pflicht und keine Telemetrie.

## Prüfkriterien

- Desktop-App startet weiter per `START.bat` und `python MethodenAnalyser3.py`.
- CLI kann Datei und Projektordner ohne GUI analysieren.
- JSON-Export ist stabil genug für Web/PWA und spätere Automationen.
- Web Companion startet lokal ohne externe Abhängigkeiten, lässt sich als PWA installieren und erzeugt dasselbe JSON-Format.
- Web Companion erklärt den LAN-/WLAN-Testpfad für Android und iOS direkt in der Oberfläche.
- Web Companion zeigt eine kopierbare PWA-Testkarte für Install-, Speicher-, Viewport- und Service-Worker-Diagnose an.
- Microsoft-Store-Paket bleibt ohne Netzwerkanforderung nutzbar.
- `releases/windowsstore/screenshots/` enthält einen reproduzierbaren Screenshot-Satz samt Manifest.
- PWA verarbeitet mindestens Snippets, einzelne Python-Dateien und kleine ZIP-Archive.
- GitHub Actions prüft denselben Quellstand jetzt auf Windows (3.10-3.12) sowie zusätzlich auf Ubuntu und macOS (3.11) per Compile-, Tkinter-Import- und `unittest`-Smoke.
