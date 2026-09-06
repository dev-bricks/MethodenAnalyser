# Security Policy / Sicherheitsrichtlinie

[English](#english) | [Deutsch](#deutsch)

---

<a name="english"></a>
## English

### Overview

**MethodenAnalyser** is a static Python code analysis suite with an offline Tkinter GUI, CLI interfaces, JSON reporting, and a local browser helper. We take security, local isolation, and developer data sovereignty seriously.

### Security Guarantees & Invariants

1. **Local-First & Zero Network Egress**:
   - MethodenAnalyser operates 100% locally and offline.
   - It performs zero external telemetry, cloud tracking, background phoning home, or remote analytics.
   - Code analysis and reporting are performed exclusively on the local machine; source code never leaves your workstation.
2. **Read-Only Source Code Analysis**:
   - Analysis runs (`--file`, `--project`, GUI inspections) treat inspected repositories and files as strictly read-only.
   - The optional Auto-Fix feature for unused imports operates only upon explicit user invocation, creating backup copies before modifications.
3. **Inert Static Analysis (No Code Execution)**:
   - Analysis relies strictly on Python's built-in `ast` parsing and textual token inspection.
   - Inspected Python files, module names, or external classes are never dynamically imported (`__import__`, `importlib`) or executed during analysis, preventing arbitrary code execution from malicious input files.
4. **Unprivileged User-Mode Execution**:
   - The desktop GUI, CLI, and local web helper run entirely in unprivileged user space.
   - No administrator rights, root privileges, or elevated system capabilities are required or requested.
5. **Local Web Helper Security Boundary**:
   - The optional web companion (`webapp/server.py`) binds strictly to local interfaces.
   - API endpoints enforce size limits, validate input types (`snippet`, `file`, `zip`), and prevent directory traversal attacks.

### Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 3.0.x   | :white_check_mark: |
| < 3.0   | :x:                |

### Reporting a Vulnerability

If you discover a security issue or vulnerability, please **do not open a public GitHub issue**. Instead, report it responsibly via:

- **GitHub Private Vulnerability Reporting**: [Report Advisory](https://github.com/dev-bricks/MethodenAnalyser/security/advisories/new)
- **Security Contact**: [security@open-bricks.org](mailto:security@open-bricks.org)
- **Maintainer Support**: [support@lukasgeiger.com](mailto:support@lukasgeiger.com)

Please provide:
- A description of the issue and potential impact
- Detailed steps to reproduce or a minimal proof of concept
- Affected versions and environment details

We acknowledge receipt within 48 hours and coordinate fixes prior to public disclosure.

---

<a name="deutsch"></a>
## Deutsch

### Übersicht

**MethodenAnalyser** ist ein statisches Python-Code-Analysewerkzeug mit lokaler Tkinter-GUI, CLI-Schnittstellen, JSON-Reporting und lokalem Browser-Hilfsmodus. Wir legen höchsten Wert auf Softwaresicherheit, lokale Isolation und die Souveränität Ihrer Quelltexte.

### Sicherheitsgarantien & Invarianten

1. **Local-First & Zero-Egress**:
   - MethodenAnalyser arbeitet zu 100 % lokal und vollständig offline.
   - Die Anwendung enthält keinerlei externe Telemetrie, Tracking, Cloud-Synchronisation oder Datenübertragung an Dritte.
   - Analysen und Berichte verbleiben ausnahmslos auf Ihrem lokalen System; Quelltexte verlassen den Arbeitsplatz nicht.
2. **Schreibschutz bei Analysen (Read-Only)**:
   - Regelreguläre Analysen (`--file`, `--project`, GUI-Scans) behandeln Quellcode und Projektordner strikt lesend.
   - Die optionale Auto-Fix-Funktion für ungenutzte Imports greift nur nach expliziter Bestätigung durch den Benutzer ein und legt Sicherheitskopien an.
3. **Inerte statische Analyse (Keine Code-Ausführung)**:
   - Die Analyse basiert rein auf dem Python `ast`-Parser und textueller Strukturinspektion.
   - Analysierte Dateien, Modulnamen oder Klassen werden niemals dynamisch importiert oder ausgeführt; dadurch werden Code-Execution-Risiken durch präparierte Eingabedateien ausgeschlossen.
4. **Ausführung mit Benutzerrechten (Unprivileged Execution)**:
   - GUI, CLI und lokaler Hilfsserver laufen vollständig im Benutzerkontext.
   - Es werden zu keinem Zeitpunkt Administratorrechte, Root-Rechte oder Systemprivilegien angefordert oder benötigt.
5. **Sicherheitsgrenzen des lokalen Web-Hilfsmodus**:
   - Der optionale Web-Begleiter (`webapp/server.py`) bindet sich an lokale Schnittstellen.
   - API-Endpunkte begrenzen Dateigrößen, validieren Eingabetypen (`snippet`, `file`, `zip`) und verhindern Pfad-Traversal-Angriffe.

### Unterstützte Versionen

| Version | Unterstützt        |
| ------- | ------------------ |
| 3.0.x   | :white_check_mark: |
| < 3.0   | :x:                |

### Sicherheitslücken melden

Wenn Sie eine Sicherheitslücke entdecken, öffnen Sie bitte **kein öffentliches Issue**. Nutzen Sie stattdessen die vertraulichen Meldewege:

- **GitHub Private Vulnerability Reporting**: [Sicherheitsbericht einreichen](https://github.com/dev-bricks/MethodenAnalyser/security/advisories/new)
- **Sicherheitskontakt**: [security@open-bricks.org](mailto:security@open-bricks.org)
- **Maintainer**: [support@lukasgeiger.com](mailto:support@lukasgeiger.com)

Bitte fügen Sie eine Beschreibung, Reproduktionsschritte, betroffene Versionen und potenzielle Auswirkungen bei. Wir bestätigen den Eingang innerhalb von 48 Stunden.
