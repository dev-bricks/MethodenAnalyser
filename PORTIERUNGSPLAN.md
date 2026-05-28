# Portierungsplan - MethodenAnalyser

Stand: 2026-05-27
Status: Windows-Store-P0 mit reproduzierbarem Screenshot-Satz, synchronisierten Store-Settings und dokumentiertem Dogfooding-Pretest abgeschlossen; CLI- und JSON-Export umgesetzt; lokale Weboberfläche bleibt Hilfs-/Demo-Modus innerhalb des Desktop-Projekts; Cross-Platform-Smoke-Automation für Windows/macOS/Linux eingerichtet

## Ausgangslage

MethodenAnalyser ist ein lokaler Python-Code-Analyser mit Tkinter-GUI und ohne externe Laufzeitabhängigkeiten. Der Kern nutzt Python-AST, Dateisystemzugriff und lokale Exporte. Dadurch ist die Desktop-Version technisch leicht auf Windows, macOS und Linux ausführbar, während mobile Plattformen wegen Dateizugriff, Projektordnern und Python-Laufzeit nicht sinnvoll als nativer Clone entwickelt werden sollten.

Die Nachfrage liegt vor allem bei Entwicklerinnen und Entwicklern, die kleine bis mittlere Python-Projekte vor Refaktorierungen, Code-Reviews oder Releases prüfen wollen. Dafür reicht eine Desktop-/Source-App: Der Kernnutzen entsteht am Entwicklungsrechner mit Projektordner, Python-Laufzeit, Editor/Terminal und lokaler Dateiablage. Ein eigener Companion-Usecase ist derzeit nicht überzeugend belegt.

## Feature-zu-Usecase-Ableitung

Ausgangspunkt ist die am besten ausgebaute Version: Desktop-App plus CLI, JSON-Export und optionale lokale Weboberfläche.

| Feature | Wann wird es gebraucht? | Usecase |
|---|---|---|
| AST-Analyse für Dateien und Projektordner | Vor Refactoring, Release, Review oder Veröffentlichung eines Python-Projekts | Lokaler Projekt-Review auf dem Entwicklungsrechner |
| Import-, Definitions- und Missing-Definition-Prüfung | Wenn ein Projekt nach Umbauten oder Copy/Paste-Änderungen auf offensichtliche Strukturfehler geprüft werden soll | Schneller statischer Qualitätscheck |
| Duplikat- und Ähnlichkeitsanalyse | Wenn ähnliche Codeblöcke vor einer Konsolidierung gefunden werden sollen | Refactoring-Vorbereitung |
| CLI-Modus mit Exit-Codes | Wenn LLMs, Scripts oder CI denselben Kern ohne GUI nutzen sollen | Automatisierter Analyse-Gate |
| `methodenanalyser-report-v1.json` | Wenn Ergebnisse aus GUI, CLI, Tests oder späteren Automationen maschinenlesbar bleiben sollen | Dateibasierter Ergebnis-Transfer und Automationsschnittstelle |
| Lokale Weboberfläche | Wenn die Analyse im Browser auf demselben Rechner demonstriert oder kurz ohne Tkinter-Fenster ausprobiert werden soll | Lokaler Demo-/Hilfsmodus, kein Companion-Produkt |

## Usecase-Settings und Plattformentscheidung

| Setting | Nutzergruppe | Plattformen | Entscheidung |
|---|---|---|---|
| Entwicklungsrechner / Projekt-Review | Entwicklerinnen, Reviewer, LLM-Automationen | Windows, macOS, Linux | Eigenständige Desktop-/Source-Linie, weil dieselben Kernusecases Dateisystem, Python-Laufzeit, Projektordner und CLI brauchen. Windows bekommt Store-Priorität; macOS/Linux bleiben Source-Smoke-Ziele. |
| Lokale Demo / Browser-Hilfsmodus | Dieselben Desktop-Nutzer auf demselben Rechner | Lokaler Browser auf Windows, macOS, Linux | Kein eigenes Usecase-Setting, sondern alternative Oberfläche innerhalb des Desktop-Projekts. Keine Produktlinie, keine eigene Release-Pipeline. |
| Mobile Nutzung | Smartphone-/Tablet-Nutzer | Android, iOS | Nicht-Ziel, weil der Kernnutzen ohne Projektordner, Python-Laufzeit und Entwicklungsumgebung wegfällt. |

Damit gibt es kein Companion-Paradigma für MethodenAnalyser. `methodenanalyser-report-v1.json` bleibt sinnvoll, aber als Automations- und Archivformat für dieselbe Desktop-Linie, nicht als Brücke zu einer mobilen App-Familie. Direkte Synchronisierung ist nicht nötig.

## Zielbild

1. Windows bleibt der primäre Release-Kanal, inklusive Microsoft Store.
2. macOS und Linux bleiben schlanke Desktop-Zielplattformen über Source-Start und Smoke-Tests.
3. Web/PWA, Android und iOS sind keine Release-Zielplattformen.
4. Die lokale Weboberfläche bleibt ein optionaler Hilfsmodus für denselben Rechner.
5. JSON-Export bleibt für Automationen, CI, LLMs und reproduzierbare Berichte erhalten.

## Plattformbewertung

| Plattform | Entscheidung | Begründung | Nächster Schritt |
|---|---|---|---|
| Windows Store | Priorität P0 | Beste Zielgruppe, vorhandene Store-Artefakte, keine externen Laufzeitabhängigkeiten | Screenshot-Satz, Listing und Dogfooding-Pretest sind fertig; als Nächstes MSIX-/WACK-Protokoll erneuern |
| Webapp / PWA | Kein eigenes Release-Ziel | Als lokale Browseroberfläche technisch vorhanden, aber kein eigenständiger Nutzer- oder Plattform-Usecase | Nur als lokales Hilfswerkzeug warten; keine Mobile-Smokes priorisieren |
| Android | Nicht-Ziel | Kein belastbarer Usecase ohne Projektordner, Python-Laufzeit und Entwicklungsumgebung | Keine Aufgaben einplanen |
| iOS | Nicht-Ziel | Gleiche Logik wie Android; Safari/PWA würde den Kernnutzen nicht tragen | Keine Aufgaben einplanen |
| macOS App | P3 | Tkinter/Python sollte laufen, aber Packaging und Signierung sind für die Zielgruppe nachrangig | Neue GitHub-Actions-Smokes für `macos-latest` beobachten; Packaging erst nach stabilen Läufen prüfen |
| Linux Version | P3 | Für Entwickler nützlich, aber Distribution über Source/ZIP reicht zunächst | Neue GitHub-Actions-Smokes für `ubuntu-latest` beobachten; Packaging erst nach stabilen Läufen prüfen |

## Architekturplan

### Desktop-Linie

- Bestehende Tkinter-App bleibt die Hauptversion.
- `analyze_file()`, `analyze_project()` und Report-Erzeugung bleiben die maßgebliche Kernlogik.
- CLI-Modus und JSON-Export bleiben die zentrale LLM-/Automationsschnittstelle.
- Bestehender Textreport bleibt erhalten; JSON ist Ergänzung, kein Plattformwechsel.

### Lokale Weboberfläche

- `webapp/server.py` bleibt als lokaler Hilfsmodus für Snippets, Einzeldateien, kleine ZIP-Archive und Report-Import erhalten.
- Die Weboberfläche ist keine Companion-App und keine eigene Android-/iOS-/Web-Produktlinie.
- Mobile Install-/Offline-Texte können bestehen bleiben, werden aber nicht weiter als Portierungsziel priorisiert.
- Kein direkter Zugriff auf beliebige lokale Projektordner im Browser; vollständige Projektanalyse bleibt Desktop-/CLI-Aufgabe.

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
4. P1: Lokale Weboberfläche für Snippet-, Einzeldatei- und kleine ZIP-Analyse als Hilfsmodus erhalten. (technisch umgesetzt 2026-05-24; kein Companion-Ziel)
5. P3: macOS- und Linux-Smoke-Tests für Source-Start automatisieren und dokumentieren. (CI-Vorbereitung erledigt 2026-05-26)
6. P2: Mobile-/Companion-Roadmap schließen und Aufgaben auf Desktop-only korrigieren. (erledigt 2026-05-28)

## Nicht-Ziele

- Kein nativer Android-Clone.
- Keine native iOS-App.
- Keine Web/PWA-Companion-Produktlinie.
- Kein vollständiger Browser-Ersatz für lokale Projektordneranalyse.
- Keine Cloud-Pflicht und keine Telemetrie.

## Prüfkriterien

- Feature-zu-Usecase-Ableitung und Usecase-Settings bleiben im Plan explizit nachvollziehbar.
- Desktop-App startet weiter per `START.bat` und `python MethodenAnalyser3.py`.
- CLI kann Datei und Projektordner ohne GUI analysieren.
- JSON-Export ist stabil genug für Automationen, CI, LLMs und spätere Desktop-Berichte.
- Lokale Weboberfläche startet weiter ohne externe Abhängigkeiten, bleibt aber Hilfsmodus.
- Microsoft-Store-Paket bleibt ohne Netzwerkanforderung nutzbar.
- `releases/windowsstore/screenshots/` enthält einen reproduzierbaren Screenshot-Satz samt Manifest.
- GitHub Actions prüft denselben Quellstand jetzt auf Windows (3.10-3.12) sowie zusätzlich auf Ubuntu und macOS (3.11) per Compile-, Tkinter-Import- und `unittest`-Smoke.
