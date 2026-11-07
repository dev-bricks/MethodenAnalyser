# MethodenAnalyser - Windows Store Build- & Packaging-Anleitung

## Voraussetzungen

1. Python 3.10+ (Standardbibliothek `ast`, `tkinter` für GUI)
2. PyInstaller für den Desktop-EXE-Build (`build_exe.bat`)
3. Windows 10/11 SDK mit `makeappx.exe`, `signtool.exe` und `appcert.exe`
4. Lokaler Schreibpfad außerhalb synchronisierter Cloud-Ordner, z. B. `C:\_Local_DEV\codex_build\methodenanalyser-store`

## Schritt 0: Store-Metadaten & Screenshots validieren

```powershell
Set-Location C:\_Local_DEV\repos\MethodenAnalyser
python scripts\check_store_readiness.py
```

Erwartetes Ergebnis:
- Alle Manifeste, Kacheln und 6-Sprachen-Metadaten PASS (0 Fehler)

## Schritt 1: Desktop-EXE mit PyInstaller bauen

```cmd
build_exe.bat
```

Ergebnis:
- `dist\MethodenAnalyser\MethodenAnalyser.exe` (Standalone-Verzeichnis)

## Schritt 2: MSIX-Paket erstellen

```powershell
$makeappx = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\makeappx.exe"
& $makeappx pack /d store_package\MethodenAnalyser /p releases\MethodenAnalyser.msix /nv
```

## Schritt 3: MSIX signieren (für lokalen Test & WACK)

```powershell
$signtool = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\signtool.exe"
& $signtool sign /fd SHA256 /a /f "$env:PFX_PATH" /p "$env:PFX_PASSWORD" /tr http://timestamp.digicert.com /td SHA256 releases\MethodenAnalyser.msix
```

## Schritt 4: Windows App Certification Kit (WACK) ausführen

```cmd
appcert.exe test -appxpackagepath releases\MethodenAnalyser.msix -reportoutputpath releases\windowsstore\test_reports\wack_report.xml
```

## Schritt 5: Partner Center Upload

1. Im Microsoft Partner Center anmelden.
2. Neues Release anlegen (Version `3.0.2.0`).
3. Pakete hochladen (`releases\MethodenAnalyser.msix`).
4. Store-Listing-Texte aus `releases\windowsstore\store_listing_<lang>.md` für alle 6 Sprachen (DE, EN, ES, ZH, JA, RU) einpflegen.
5. Screenshots aus `releases\windowsstore\screenshots\` hochladen.
6. Zur Zertifizierung einreichen.
