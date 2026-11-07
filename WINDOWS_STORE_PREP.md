# Windows Store Preparation & Packaging Guide — MethodenAnalyser

Stand: 2026-11-07

## Übersicht

MethodenAnalyser wird als modernes MSIX-Paket für den Microsoft Store bereitgestellt. Das Desktop-Bridge-Paket kapselt die lokale Python-Desktop-Anwendung in einer sicheren, offline-fähigen Windows-Desktop-Container-Umgebung.

## Metadaten & Identität

| Eigenschaft | Wert |
|---|---|
| **Identity Name** | `Geiger.MethodenAnalyser` |
| **Publisher** | `CN=52596601-BAB4-4F3F-B182-E8F3F273B202` |
| **Publisher Display** | `Lukas Geiger` |
| **Paket-Version** | `3.0.2.0` |
| **Kategorie** | `Developer Tools` |
| **Capabilities** | `runFullTrust`, `internetClient` |
| **Deklarierte Sprachen** | `de-DE`, `en-US`, `es-ES`, `zh-CN`, `ja-JP`, `ru-RU` |
| **Executable** | `MethodenAnalyser.exe` |

## Erledigte Vorbereitungsschritte

1. **Paketierungs-Metadaten (`store_package.json` & `store_settings.json`):**
   - Vollständige Publisher-DN, Identity-Name und Version synchronisiert.
   - Alle 6 Zielsprachen (Tier-2 nach Policy P-006) deklariert.
   - Kurzbeschreibungen für alle 6 Sprachen strikt <= 100 Zeichen.
   - Exakt 7 Schlüsselwörter je Sprache nach Microsoft Partner Center Policy 10.1.3 (jeweils <= 30 Zeichen, strikt keine geschützten Drittmarken).
   - Öffentliche HTTPS Privacy- und Support-URLs hinterlegt.

2. **Desktop Bridge Manifest (`store_package/MethodenAnalyser/AppxManifest.xml`):**
   - Schema-konforme Deklaration für `Windows.Desktop` (MinVersion `10.0.17763.0`, MaxVersionTested `10.0.26100.0`).
   - Alle 6 Sprach-Ressourcen deklariert (`de-de`, `en-us`, `es-es`, `zh-cn`, `ja-jp`, `ru-ru`).
   - StoreLogo (50x50), Square150x150Logo, Square44x44Logo, Wide310x150Logo und Square310x310Logo korrekt gebunden.

3. **Staging-Dateien (`releases/windowsstore/`):**
   - `BUILD.md` und `WACK_PROTOCOL.md` mit reproduzierbaren Build- und Prüfbefehlen.
   - 6 lokalisierte Store-Listings (`store_listing_<lang>.md`).
   - Kacheln und `StoreLogo.png` im Staging-Ordner hinterlegt.
   - Screenshots in `releases/windowsstore/screenshots/` mit `manifest.json`.

4. **Automatisierter Readiness-Check (`scripts/check_store_readiness.py`):**
   - Prüft alle Dokumente, Manifest-Invarianten, Kachel-Dimensionen und Keyword-Policies hermetisch im Testlauf.

## Checkliste vor Store-Einreichung

- [x] Lokale PyInstaller-EXE gebaut und im isolierten Start-Smoke geprüft
- [x] Alle Store-Kacheln in exakten Pixel-Dimensionen vorhanden
- [x] 6-Sprachen-Parität in Manifest, Listing und `locales/translations.json` (100%)
- [x] Kurzbeschreibungen <= 100 Zeichen, Keywords nach Richtlinie 10.1.3
- [x] Readiness-Audit `python scripts/check_store_readiness.py` erfolgreich (0 Fehler)
- [ ] Erhöhter WACK-Lauf als Administrator vor finalem Upload
- [ ] Partner Center MSIX-Upload und Review-Start
