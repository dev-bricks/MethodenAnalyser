# Beitragsrichtlinie / Contributing Guide

**[Deutsch](#deutsch)** | **[English](#english)**

---

<a name="deutsch"></a>
## Deutsch

Vielen Dank für Ihr Interesse, zu **MethodenAnalyser** beizutragen. MethodenAnalyser ist ein lokales, zustandsloses Open-Source-Analysewerkzeug für Python-Codebasen im Ökosystem von `dev-bricks` und `open-bricks`.

### 1. Grundprinzipien & Laufzeit-Invarianten

Alle Beiträge müssen die folgenden 10 architektonischen und sicherheitsbezogenen Invarianten einhalten:

1. **INV-LOCAL-01 (100% Local-First & Zero-Egress):** Keine ausgehenden Netzwerkaufrufe, keine Telemetrie, keine externen Sockets.
2. **INV-SECURITY-02 (Non-Elevation / RunAsInvoker):** Ausschließliche Ausführung im Standard-Benutzermodus. Niemals Administrator- oder Root-Rechte anfordern.
3. **INV-AST-03 (Inerte statische AST-Analyse):** Analyse rein über `ast.parse()`. Zielmodule werden niemals dynamisch importiert oder ausgeführt.
4. **INV-ENCODING-04 (Verlustfreie Kodierung):** UTF-8 als Standard mit Latin-1-Fallback; UTF-8 BOM und deutsche Umlaute müssen verlustfrei erhalten bleiben.
5. **INV-ISOLATION-05 (Loopback-Web-Isolation):** Der lokale Web-Begleiter bindet standardmäßig ausschließlich an `127.0.0.1`.
6. **INV-TRAVERSAL-06 (Schutz vor Pfad-Traversal & ZIP-Bomben):** Ablehnung von `..`, strikte Begrenzung von Archivgröße und Dateianzahl.
7. **INV-AUTOFIX-07 (Reversibler Auto-Fix mit Backup):** Auto-Fix erfordert Bestätigung, prüft Quelltext vor Ersetzung erneut und legt atomare `.bak`-Sicherungen an.
8. **INV-PLATFORM-08 (Plattformübergreifende Standardbibliothek-Parität):** 100% Standardbibliothek; verifiziert auf Windows, Ubuntu Linux und macOS.
9. **INV-SYNC-09 (Multi-Host Lock- & Cloud-Sync-Schutz):** Fail-closed bei aktiven Locks (`LOCK.*`); Ignorieren von Cloud-Sync-Konfliktdateien.
10. **INV-SLA-10 (48h-Sicherheits-SLA & 5-Werktage-Triage):** Verbindliche Melde- und Triage-Zusage gemäß [SECURITY.md](SECURITY.md).

### 2. Lokaler Entwicklungsworkflow (Plan D)

- **Kanonischer Arbeitsort (Source of Truth):** `C:\_Local_DEV\repos\MethodenAnalyser` (lokaler Git-Klon).
- **OneDrive-Rolle:** Nur gitloser Spiegel für Multi-Device-Verfügbarkeit. Niemals originär im Cloud-Synchronisationsordner entwickeln.

### 3. Qualitäts-Tore vor jedem Commit & PR

Vor dem Öffnen eines Pull Requests oder dem Pushen müssen alle Qualitäts-Tore lokal bestanden sein:

```bash
# 1. Bytecode- & Syntax-Prüfung
python -m compileall -q .

# 2. Linter & Format-Check
ruff check .

# 3. Testsuite (100% grün)
pytest -ra -v
```

### 4. Pull-Request-Verfahren

1. Forken Sie das Repository: `https://github.com/dev-bricks/MethodenAnalyser`.
2. Erstellen Sie einen Feature-Branch: `git checkout -b feature/mein-feature`.
3. Committen Sie Ihre Änderungen unter Beachtung der Invarianten: `git commit -m "feat: beschreibung"`.
4. Pushen Sie den Branch und öffnen Sie einen PR gegen den Branch `master`.

### 5. Gesetzlicher Hinweis & Haftungsausschluss

Beiträge erfolgen im Rahmen einer unentgeltlichen Open-Source-Schenkung (§§ 516 ff. BGB). Gemäß **§ 521 BGB** ist die Haftung auf Vorsatz und grobe Fahrlässigkeit beschränkt.

---

<a name="english"></a>
## English

Thank you for your interest in contributing to **MethodenAnalyser**. MethodenAnalyser is an offline-first, local Python code analyzer within the `dev-bricks` and `open-bricks` ecosystem.

### 1. Foundational Architecture & Runtime Invariants

All pull requests and contributions must strictly adhere to the 10 runtime invariants:

1. **INV-LOCAL-01 (100% Local-First & Zero-Egress):** Zero outbound network calls, telemetry, analytics, or background sockets.
2. **INV-SECURITY-02 (Non-Elevation / RunAsInvoker):** Executes strictly in standard user space. Never request or require administrative/root elevation.
3. **INV-AST-03 (Inert Static AST Parsing):** Static code analysis via Python `ast.parse()`. Target modules are never executed or dynamically imported.
4. **INV-ENCODING-04 (Lossless Multi-Encoding Resilience):** Default UTF-8 reading with Latin-1 fallback; preserves BOMs, encoding styles, and unicode characters.
5. **INV-ISOLATION-05 (Loopback Web Isolation):** The local web companion binds strictly to `127.0.0.1` by default.
6. **INV-TRAVERSAL-06 (Anti-Path-Traversal & ZIP Safety):** Rejection of directory traversal (`..`), bounds on member count and archive byte size.
7. **INV-AUTOFIX-07 (Reversible Auto-Fix with Atomic Backup):** Auto-fix requires confirmation, rechecks current AST usage, and creates byte-exact `.bak` backups before atomic replacement.
8. **INV-PLATFORM-08 (Cross-Platform Standard Library Parity):** 100% standard library core verified on Windows, Linux, and macOS.
9. **INV-SYNC-09 (Multi-Host Lock & Cloud-Sync Safety):** Fails closed upon encountering active lock files (`LOCK.*`); ignores sync conflict artifacts.
10. **INV-SLA-10 (48h Security Response SLA & 5-Day Triage):** Committed security response and triage SLA documented in [SECURITY.md](SECURITY.md).

### 2. Local Development Workflow (Plan D)

- **Canonical Workspace (Source of Truth):** `C:\_Local_DEV\repos\MethodenAnalyser` (local git clone).
- **Cloud-Storage Role:** Cloud folders are strictly gitless projections/mirrors for multi-device access. Never develop directly inside synchronized cloud directories.

### 3. Pre-Commit Quality Gates

Verify the entire quality gate suite locally before committing:

```bash
# 1. Bytecode compilation
python -m compileall -q .

# 2. Linter check
ruff check .

# 3. Automated test suite (100% green)
pytest -ra -v
```

### 4. Pull Request Procedure

1. Fork the repository: `https://github.com/dev-bricks/MethodenAnalyser`.
2. Create a feature branch: `git checkout -b feature/my-feature`.
3. Commit changes with conventional commit syntax: `git commit -m "feat: description"`.
4. Push the branch and open a PR against `master`.

### 5. Statutory Disclaimer

This project is a gratuitous open-source donation under German Civil Code §§ 516 ff. BGB. Under **§ 521 BGB**, statutory liability is limited to intent and gross negligence.
