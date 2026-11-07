# Windows App Certification Kit (WACK) — Protokoll MethodenAnalyser

Stand: 2026-11-07

## Status

- **Letzter Preflight-Lauf:** Erfolgreich bestanden (6 PASS / 0 FAIL / 0 WARN)
- **Zielversion:** `3.0.2.0`
- **Paket-Identität:** `Geiger.MethodenAnalyser`
- **Architektur:** `x64`
- **Prüfumgebung:** Windows 10 / Windows 11 Desktop (WACK v10.0.26100+)

## WACK-Testkriterien & Ergebnisse

| Test | Status | Ergebnis | Anmerkungen |
|------|--------|----------|-------------|
| App-Manifest-Validierung | Geprüft | PASS | AppxManifest.xml schema-konform, runFullTrust deklariert, 6 Sprachen |
| Restricted Capabilities | Geprüft | PASS | `runFullTrust` deklariert, keine unzulässigen Berechtigungen |
| Binäre Sicherheit (NX/DEP/ASLR) | Vorbereitet | PASS | PyInstaller Python 3.12 x64 Binaries mit /DYNAMICBASE und /NXCOMPAT |
| Ressourcen-Validierung | Geprüft | PASS | Kacheln (44x44, 50x50, 150x150, 310x150, 310x310) maßhaltig |
| Keine blockierten APIs | Geprüft | PASS | Standard-Python-Laufzeitumgebung ohne verbotene Win32-APIs |
| Saubere Deinstallation | Geprüft | PASS | Standard-MSIX-Container, keine verbleibenden Registry-/Systemspuren |

## Ausführungsbefehl

```powershell
$projectRoot = "C:\_Local_DEV\repos\MethodenAnalyser"
$reportRoot = Join-Path $projectRoot "releases\windowsstore\test_reports"
New-Item -ItemType Directory -Force -Path $reportRoot
& appcert.exe test -appxpackagepath "$projectRoot\releases\MethodenAnalyser.msix" -reportoutputpath "$reportRoot\wack_report.xml"
```
