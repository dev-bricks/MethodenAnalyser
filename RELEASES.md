# RELEASES - MethodenAnalyser

Stand: 2026-05-01
Aktuelles lokales EXE-Bundle: `v3.0.0`

## Struktur

```text
releases/
|-- v3.0.0/
|   |-- MethodenAnalyser-3.0.0-win64.exe
|   |-- MethodenAnalyser-3.0.0-source.zip
|   |-- CHANGELOG.txt
|   `-- SHA256SUMS.txt
`-- windowsstore/
    `-- ...
```

## Aktueller Stand

- `dist/MethodenAnalyser.exe` ist der frische lokale Build aus dem aktuellen Quellstand.
- `releases/v3.0.0/` enthält die lokalen GitHub-/Direktdownload-Artefakte.
- `releases/windowsstore/` bleibt getrennt für den MSIX-/Store-Workflow.
- Der Ordner `releases/` ist absichtlich per `.gitignore` ausgeschlossen. Verteilbare Binärartefakte gehören in lokale Release-Ordner oder GitHub Releases, nicht in den Git-Quellbaum.

## Letzte Pflege

- 2026-04-29: Lokales EXE-Bundle, Source-ZIP und Checksummen aus dem aktuellen Arbeitsstand aktualisiert.
- 2026-05-01: Release-Dokumentation an die GitHub-Policy angepasst: Artefakte bleiben lokal oder in GitHub Releases.
