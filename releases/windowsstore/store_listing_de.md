Kurzbeschreibung:
Statischer Python-Code-Analyser für ungenutzte Imports, Definitionen und Code-Duplikate.

Beschreibung:
MethodenAnalyser ist ein spezialisierter statischer Code-Analyser für Python-Projekte. Er analysiert Python-Quellcode präzise über den Abstract Syntax Tree (AST), spürt ungenutzte Imports und tote Funktionen auf und erkennt Code-Duplikate.

Hauptfunktionen:
- AST-basierte statische Analyse ohne externe Abhängigkeiten
- Zuverlässige Erkennung ungenutzter Imports mit automatischem Auto-Fix und Backup-Sicherung
- Methoden- und Funktionskatalog mit detailliertem Verwendungsstatus
- Ähnlichkeits- und Duplikaterkennung mit konfigurierbarem Schwellwert
- Framework-Awareness für Callback-Funktionen (Tkinter, requests, asyncio u. a.)
- Rekursive Multi-File-Projektanalyse mit strukturierter Zusammenfassung
- Headless-CLI-Modus und maschinenlesbarer JSON-Export (methodenanalyser-report-v1.json)
- Lokale, datenschutzfreundliche Ausführung ohne Cloud-Zwang

Zielgruppe:
Python-Entwickler, Code-Reviewer und Teams, die gewachsene Codebasen bereinigen, Refactorings vorbereiten und Clean-Code-Standards wahren wollen. Lizenz: MIT.

Keywords:
Code-Analyse, AST-Parser, Ungenutzte Imports, Duplikat-Erkennung, Refactoring, Clean Code, Entwickler-Tools
