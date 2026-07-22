# RELEASES - MethodenAnalyser

Stand: 2026-07-22
Direktdownload-Bundle `v3.0.0`: **gesperrter Legacy-Stand, nicht aktuell freigegeben**.

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

## Aktueller Stand und Abgrenzung

- `releases/v3.0.0/` enthält historische lokale GitHub-/Direktdownload-Artefakte. Ihr genauer Auditstand steht in [`releases/v3.0.0/PROVENANCE.md`](releases/v3.0.0/PROVENANCE.md).
- `dist/MethodenAnalyser.exe` ist derzeit nicht vorhanden. Ein Root-EXE oder ein historisches v3.0.0-EXE darf deshalb nicht als frischer `dist`-Build ausgegeben werden.
- Das v3.0.0-EXE weicht von der gespeicherten SHA-256-Zeile ab; Source-ZIP und Changelog haben keinen belegten Quellcommit. Bis zu einem sauberen Neubuild mit Commit- und Hashnachweis ist das Bundle nicht für Direktdownload oder Promotion freigegeben.
- `releases/windowsstore/` bleibt getrennt für den MSIX-/Store-Workflow.
- Das MSIX-/WACK-Gate ist ein eigener Ablauf und ersetzt keine Direktdownload-Provenienz.
- Der Ordner `releases/` ist absichtlich per `.gitignore` ausgeschlossen. Verteilbare Binärartefakte gehören in lokale Release-Ordner oder GitHub Releases, nicht in den Git-Quellbaum.

## Nächster freigegebener Buildablauf

1. Einen konkreten, geprüften Quellcommit und die Buildumgebung festhalten.
2. EXE, Source-ZIP und Changelog aus genau diesem Stand erzeugen und ihren Start-/Inhaltscheck dokumentieren.
3. Erst dann `SHA256SUMS.txt` ausschließlich aus diesem vollständigen Artefaktsatz erzeugen, gegenlesen und eine neue Aktualitätsentscheidung treffen.
4. Store/MSIX nur als separaten, zusätzlich zu belegenden Gate-Schritt behandeln.

## Letzte Pflege

- 2026-07-22: Provenienz-Audit: v3.0.0 wegen fehlender Commit-Kette und abweichender EXE-Checksumme gesperrt; keine Dateien gelöscht, keine neue Version oder neue Checksumme erzeugt.
- 2026-05-01: Release-Dokumentation an die GitHub-Policy angepasst: Artefakte bleiben lokal oder in GitHub Releases.
