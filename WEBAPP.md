# MethodenAnalyser Lokale Weboberfläche

Stand: 2026-05-24

Die lokale Weboberfläche ist ein Hilfs-/Demo-Modus für schnelle Snippet-, Einzeldatei- und kleine ZIP-Analysen auf demselben Rechner. Sie ersetzt nicht die Desktop-App für ganze Projektordner, ist keine Companion-App und keine eigene Mobile-Produktlinie. Sie nutzt denselben Analysekern und dasselbe JSON-Format wie CLI und GUI.

## Start

```bash
python webapp/server.py
```

Unter Windows kann alternativ `START_WEBAPP.bat` per Doppelklick gestartet werden.

Standard-Adresse:

```text
http://127.0.0.1:8765/
```

Optionale Parameter:

```bash
python webapp/server.py --host 127.0.0.1 --port 8765
```

Für Android-/iOS-Tests im selben WLAN:

```bash
python webapp/server.py --host 0.0.0.0 --port 8765
```

Die Oberfläche kann dann erkannte LAN-URLs anzeigen. Das ist nur ein technischer Testpfad für lokale Browser-Smokes, kein geplanter Android-/iOS-Releasepfad.

## Funktionen

- Python-Code in das Textfeld einfügen und lokal analysieren.
- Einzelne `.py`-Dateien im Browser öffnen und analysieren.
- Kleine `.zip`-Archive mit Python-Dateien lokal hochladen und als Mini-Projekt analysieren.
- Textreport direkt anzeigen.
- JSON-Report im Schema `methodenanalyser-report-v1.json` anzeigen, speichern und wieder importieren.
- Entwurf und letzter JSON-Report lokal im Browser zwischenspeichern.
- PWA installieren und nach der ersten Nutzung offline erneut öffnen.
- Statische PWA-Dateien mit Service Worker cachen; die Analyse-API bleibt lokal und wird nicht gecacht.

## Browser-Verhalten

- Chrome und Edge können die Oberfläche als installierbare PWA anbieten.
- Für lokale Browser-Smokes zeigt die Oberfläche den empfohlenen LAN-Startbefehl und, falls erkannt, direkte URLs zum Kopieren.
- Die **PWA-Testkarte** bündelt App-Modus, Install-Flow, Service-Worker-Status, lokalen Speicher, Viewport und den erkannten Serverpfad in einer kopierbaren Kurzdiagnose.
- Bereits geladene Oberfläche bleibt durch den Service Worker auch ohne laufenden Server erreichbar.
- Neue Analysen benötigen weiter den lokalen Python-Prozess; offline bleiben Entwurf, letzter JSON-Report, importierte Reports und die UI verfügbar.
- Android und iOS sind keine Zielplattformen; es gibt keine native App, keine Mobile-Roadmap und keinen Cloud-Sync.

## Lokale API

`POST /api/analyze`

Request:

```json
{
  "source_kind": "snippet",
  "filename": "<snippet>",
  "code": "import os\nprint('ok')\n"
}
```

`source_kind` ist aktuell `snippet`, `file` oder `zip`.

Für ZIP-Analysen wird statt `code` ein Base64-Feld `zip_base64` gesendet. Das Archiv bleibt lokal, wird temporär entpackt und nur auf `.py`-Dateien geprüft.

Response:

```json
{
  "ok": true,
  "has_findings": true,
  "text_report": "...",
  "report": {
    "schema_version": "methodenanalyser-report-v1"
  }
}
```

## Datenschutz

Der Web Companion läuft auf `127.0.0.1`. Code wird an den lokalen Python-Prozess gesendet, nicht an externe Dienste. Es gibt keine Telemetrie, keine Cloud-Synchronisierung und keine externen CDN-Abhängigkeiten.

## Grenzen

- Große Projektordner bleiben Aufgabe der Desktop-/CLI-Version.
- ZIP-Uploads sind bewusst klein gehalten: nur `.py`-Dateien, begrenzte Archivgröße und keine beliebigen Binärdateien.
- Android und iOS sollen über dieselbe PWA-Linie getestet werden; native Apps sind weiterhin kein Ziel.
