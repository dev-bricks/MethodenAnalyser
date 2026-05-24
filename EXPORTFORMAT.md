# EXPORTFORMAT - methodenanalyser-report-v1.json

Stand: 2026-05-24

Dieses Dokument beschreibt das JSON-Austauschformat für MethodenAnalyser. Das Format verbindet die lokale Desktop-/CLI-Version mit späteren Web-, Android- und iOS-PWA-Companions. Der bestehende Textreport bleibt unverändert; JSON ist eine zusätzliche maschinenlesbare Ausgabe.

## Ziel

- Datei-, Projekt- und Snippet-Analysen einheitlich serialisieren.
- Ergebnisse ohne absolute lokale Pfade weitergeben.
- Ein stabiles Format für Automationen, Store-Demos und PWA-Prototypen bereitstellen.
- Datenschutzfreundlich bleiben: Quellcode wird nicht in den Report geschrieben, nur Analyseergebnisse.

## CLI-Ausgabe

```bash
python MethodenAnalyser3.py --file beispiel.py --json-output
python MethodenAnalyser3.py --project pfad/zum/projekt --json-output report.json
type beispiel.py | python MethodenAnalyser3.py --stdin --json-output snippet.json
```

Ohne Dateiwert schreibt `--json-output` nach `methodenanalyser-report-v1.json`.

## Top-Level-Felder

| Feld | Typ | Beschreibung |
|---|---|---|
| `schema_version` | string | Aktuell immer `methodenanalyser-report-v1`. |
| `tool_version` | string | MethodenAnalyser-Version, aktuell `3.0`. |
| `source_kind` | string | `file`, `project`, `snippet` oder `zip`. |
| `generated_at` | string | UTC-Zeitstempel im ISO-Format. |
| `source` | object | Quellkontext ohne absolute Pfade in `files[]`. |
| `files` | array | Einzelanalysen pro Datei oder Snippet. |
| `unused_imports` | object | Map `relativer_pfad -> Liste`. |
| `unused_definitions` | object | Map `relativer_pfad -> Liste`. |
| `missing_definitions` | object | Map `relativer_pfad -> Liste`. |
| `missing_imports` | object | Map `relativer_pfad -> Liste`. |
| `duplicate_imports` | object | Map `relativer_pfad -> Liste`. |
| `summary` | object | Verdichtete Zählwerte. |
| `errors` | array | Nur bei Projektanalyse mit nicht analysierbaren Dateien. |

## files[]-Eintrag

```json
{
  "path": "beispiel.py",
  "analysis": {
    "summary": {
      "calls": 2,
      "definitions": 1,
      "imports": 1,
      "unused_imports": 0,
      "unused_definitions": 0,
      "missing_definitions": 0,
      "missing_imports": 0,
      "duplicate_imports": 0,
      "todos": 0
    },
    "calls": ["print"],
    "definitions": ["main"],
    "imports": ["json"],
    "unused_imports": [],
    "unused_definitions": [],
    "missing_definitions": [],
    "missing_imports": [],
    "duplicate_imports": [],
    "todos": []
  }
}
```

## Stabilitätsregeln

- Neue Felder dürfen ergänzt werden, bestehende Feldnamen bleiben für `methodenanalyser-report-v1` stabil.
- PWA- oder Server-Companions dürfen `source_kind = "snippet"` und `source_kind = "zip"` nutzen.
- Projektberichte verwenden relative Pfade ab Projektwurzel und normalisieren Trenner auf `/`.
- Fehlerhafte Dateien erscheinen in `errors`, erfolgreiche Dateien weiter in `files`.
