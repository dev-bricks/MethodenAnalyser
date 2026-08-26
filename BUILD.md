# MethodenAnalyser — reproduzierbarer Dev-/Build-Vertrag

Stand: 2026-08-26

## Toolchain

Die Runtime bleibt Python-Standardbibliothek-only. Entwicklungs- und
Build-Werkzeuge werden getrennt installiert:

```powershell
python -m pip install -r requirements-dev.txt
python -m pip show pytest pyinstaller
```

`requirements-dev.txt` definiert den getesteten Bereich:

| Werkzeug | Unterstützter Bereich | Smoke-Readback |
|---|---|---|
| pytest | `>=9.0.3,<10.0` | 9.1.1 (2026-08-26) |
| PyInstaller | `>=6.14.2,<7.0` | 6.21.0 (2026-08-26) |

Eine andere Version ist möglich, aber nicht durch diesen Vertrag verifiziert.

## Test-Smoke

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
python -m py_compile MethodenAnalyser3.py manage_translations.py translator.py webapp/server.py
python -m unittest discover -s tests -v
```

GitHub Actions prüft Python 3.10, 3.11 und 3.12 auf Windows sowie Python 3.11
auf Ubuntu und macOS. `tkinter` muss in der jeweiligen Python-Installation
vorhanden sein.

## EXE-Build

```powershell
cmd /c build_exe.bat
```

Das Skript ruft PyInstaller direkt für `MethodenAnalyser3.py` mit
`--windowed --onefile` auf; die eingecheckte `MethodenAnalyser.spec` wird von
diesem Batch-Pfad nicht eingelesen. Der zentrale `build_exclude_scanner.py`
wird verwendet, wenn er im erwarteten `_tools`-Pfad vorhanden ist;
andernfalls meldet das Skript den Fallback und baut ohne dynamische Excludes.

Arbeits- und primäre Ausgabe liegen unter
`C:\_Local_DEV\codex_build\methodenanalyser\`. Nach erfolgreichem Build kopiert
das Skript die EXE zusätzlich nach `dist\MethodenAnalyser.exe` und
`MethodenAnalyser.exe` im Projekt. Diese lokalen Artefakte sind kein Release.

MSIX, Signierung, WACK, Store-Upload und Release-Registrierung sind getrennte,
manuell freizugebende Schritte. Dieses Dokument führt sie nicht automatisch
aus.
