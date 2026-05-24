# Portierungsplan - MethodenAnalyser

Stand: 2026-05-24  
Status: CLI-, JSON-Export und lokaler Web/PWA-Prototyp umgesetzt

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
| Windows Store | Priorität P0 | Beste Zielgruppe, vorhandene Store-Artefakte, keine externen Laufzeitabhängigkeiten | Store-Screenshots, Listing, Dogfooding-Build und Pre-Submission prüfen |
| Webapp / PWA | Priorität P1 | Gute Demo- und Companion-Linie für Snippets, einzelne Dateien und kleine Uploads | Lokalen Prototyp unter `webapp/` dogfooden und danach ZIP-Upload bewerten |
| Android | P2 über PWA | Native App wäre Mehraufwand ohne klaren Mehrwert; PWA reicht für mobile Kurzchecks | Web Companion auf Android-Browser testen |
| iOS | P2 über PWA | Gleiche Logik wie Android; nativer App-Store-Weg lohnt aktuell nicht | Web Companion auf iOS Safari testen |
| macOS App | P3 | Tkinter/Python sollte laufen, aber Packaging und Signierung sind für die Zielgruppe nachrangig | Source-Smoke-Test und optionales PyInstaller-Bundle prüfen |
| Linux Version | P3 | Für Entwickler nützlich, aber Distribution über Source/ZIP reicht zunächst | Source-Smoke-Test und README-Hinweis ergänzen |

## Architekturplan

### Desktop-Linie

- Bestehende Tkinter-App bleibt die Hauptversion.
- `analyze_file()`, `analyze_project()` und Report-Erzeugung bleiben die maßgebliche Kernlogik.
- Ergänzt werden sollte ein CLI-Modus, damit dieselbe Analyse ohne GUI für Tests, Automationen und spätere Web/PWA-Brücken nutzbar ist.
- Bestehender Textreport bleibt erhalten; zusätzlich wird ein JSON-Export eingeführt.

### Web/PWA-Linie

- Start als getrennte, kleine Companion-App, nicht als Umbau der Desktop-GUI.
- Erste Ausbaustufe umgesetzt: Code-Paste und einzelne `.py`-Dateien laufen über einen lokalen stdlib-Python-Dienst unter `webapp/server.py`.
- Kein direkter Zugriff auf beliebige lokale Projektordner im Browser.
- Export/Import über `methodenanalyser-report-v1.json`.
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

1. P0: Windows-Store-Vorbereitung abschließen.
2. P0: CLI-Modus für Datei- und Projektanalyse ergänzen. (erledigt 2026-05-24)
3. P1: JSON-Export `methodenanalyser-report-v1.json` aus Desktop-Kernlogik erzeugen. (erledigt 2026-05-24)
4. P1: PWA-Prototyp für Snippet- und Einzeldatei-Analyse umsetzen. (erledigt 2026-05-24)
5. P2: Android-/iOS-Browsertests für die PWA durchführen.
6. P3: macOS- und Linux-Smoke-Tests für Source-Start dokumentieren.

## Nicht-Ziele

- Kein nativer Android-Clone.
- Keine native iOS-App.
- Kein vollständiger Browser-Ersatz für lokale Projektordneranalyse.
- Keine Cloud-Pflicht und keine Telemetrie.

## Prüfkriterien

- Desktop-App startet weiter per `START.bat` und `python MethodenAnalyser3.py`.
- CLI kann Datei und Projektordner ohne GUI analysieren.
- JSON-Export ist stabil genug für Web/PWA und spätere Automationen.
- Web Companion startet lokal ohne externe Abhängigkeiten und erzeugt dasselbe JSON-Format.
- Microsoft-Store-Paket bleibt ohne Netzwerkanforderung nutzbar.
- PWA verarbeitet mindestens Snippets und einzelne Python-Dateien.
