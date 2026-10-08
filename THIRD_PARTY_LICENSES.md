# Third-Party Licenses & Dependencies / Drittanbieter-Lizenzen

**Stand / Audited:** 2026-10-08 | **Version:** 3.0.2 | **Lizenz:** MIT | **Modus:** RunAsInvoker

This document lists all dependencies, runtime requirements, and third-party licenses for **MethodenAnalyser**.

---

## 1. Runtime Dependencies: Zero External Dependencies (100% Python Standard Library)

MethodenAnalyser is engineered as a **zero-dependency, offline-first tool**. It does not require or bundle any third-party runtime libraries.

All core functionality is implemented exclusively using the Python Standard Library (Python 3.10+):

| Module | Purpose | License |
|---|---|---|
| `ast` | Abstract Syntax Tree parsing and lexical traversal | Python Software Foundation License (PSFL) |
| `tkinter` | Native cross-platform desktop graphical user interface | Python Software Foundation License (PSFL) |
| `difflib` | `SequenceMatcher` algorithm for code duplicate and similarity detection | Python Software Foundation License (PSFL) |
| `http.server` | Lightweight local loopback companion server (`127.0.0.1`) | Python Software Foundation License (PSFL) |
| `json` | Structured report serialization (`methodenanalyser-report-v1.json`) | Python Software Foundation License (PSFL) |
| `pathlib` / `os` / `sys` | File system navigation, path resolution, and platform checks | Python Software Foundation License (PSFL) |
| `re` | Regular expression matching and tokenization | Python Software Foundation License (PSFL) |
| `sqlite3` | Local report caching and indexing | Python Software Foundation License (PSFL) |
| `threading` | Non-blocking GUI background task processing | Python Software Foundation License (PSFL) |

Because no external runtime packages are required, MethodenAnalyser has **zero runtime supply-chain attack surface** and requires no network downloads (`pip install`) for production usage.

---

## 2. Development & Quality Assurance Toolchain

The following tools are used strictly during development, automated testing, and release packaging. They are **not** bundled into the runtime distribution:

| Tool | Version Range | Purpose | License | Repository / Source |
|---|---|---|---|---|
| **pytest** | `>=9.1.1` | Automated test runner & assertions (CVE-2025-7117 hardened) | MIT License | [pytest-dev/pytest](https://github.com/pytest-dev/pytest) |
| **ruff** | `>=0.9.0` | Fast Python linter & code formatter | MIT / Apache 2.0 | [astral-sh/ruff](https://github.com/astral-sh/ruff) |
| **PyInstaller** | `>=6.10.0` | Windows portable EXE compilation (`build_exe.bat`) | GPL-2.0 / Special Exception | [pyinstaller/pyinstaller](https://github.com/pyinstaller/pyinstaller) |
| **altgraph** | `>=0.17.4` | Dependency graph analysis for PyInstaller | MIT License | [ronaldoussoren/altgraph](https://github.com/ronaldoussoren/altgraph) |
| **packaging** | `>=24.0` | Core Python package version utilities | Apache-2.0 / BSD-2-Clause | [pypa/packaging](https://github.com/pypa/packaging) |

---

## 3. Project License

MethodenAnalyser itself is open-source software licensed under the **MIT License**.

See [LICENSE](LICENSE) for the full text.

---

## 4. Governance & Runtime Invariants Verification Matrix (Stand: 2026-10-08)

| Invariant | Title | Verification Status & Enforcement |
|---|---|---|
| **INV-LOCAL-01** | 100% Local-First & Zero-Egress | **VERIFIED** — Zero outbound network calls, telemetry, or analytics. |
| **INV-SECURITY-02** | Non-Elevation / RunAsInvoker | **VERIFIED** — Unprivileged user mode; zero administrative elevation. |
| **INV-AST-03** | Inert Static AST Parsing | **VERIFIED** — Pure `ast.parse()`; target modules are never executed. |
| **INV-ENCODING-04** | Lossless Multi-Encoding Resilience | **VERIFIED** — UTF-8 primary, Latin-1 fallback, preserves BOM and umlauts. |
| **INV-ISOLATION-05** | Loopback Web Companion Isolation | **VERIFIED** — Default loopback `127.0.0.1` binding; `--host 0.0.0.0` requires explicit user flag. |
| **INV-TRAVERSAL-06** | Anti-Path-Traversal & ZIP Safety Bounds | **VERIFIED** — Rejects traversal (`..`), bounds member count and max byte size. |
| **INV-AUTOFIX-07** | Reversible Auto-Fix with Atomic Backup | **VERIFIED** — Rechecks usage, writes atomic `.bak`, flushed temporary writes. |
| **INV-PLATFORM-08** | Multi-Platform Parity | **VERIFIED** — 100% Python Standard Library verified on Windows, Linux, macOS 26. |
| **INV-SYNC-09** | Multi-Host Lock & Sync Safety | **VERIFIED** — Fails closed on `LOCK.*`; ignores cloud sync conflicts (`*-conflict-*`). |
| **INV-SLA-10** | 48h Security Response SLA & 5-Day Triage | **VERIFIED** — Vulnerability response commitment documented in [SECURITY.md](SECURITY.md). |

---

## 5. Unprivileged Execution Mode Certification (INV-SECURITY-02)

MethodenAnalyser is certified for standard unprivileged user-mode execution (**RunAsInvoker**). The application does not require, request, or invoke administrative, root, or elevated operating system privileges. Code analysis operates entirely via inert AST parsing and does not execute target files.

---

## 6. Statutory Notice (§ 521 BGB Gefälligkeitsrecht) & Security Contacts

This project is an open-source contribution provided free of charge ("unentgeltliche Open-Source-Schenkung" under German Civil Code §§ 516 ff. BGB). Under German law (**§ 521 BGB**), liability is limited to intent and gross negligence.

**Coordinated Vulnerability Disclosure & Contacts:**
- **GitHub Advisory:** [Report a private vulnerability](https://github.com/dev-bricks/MethodenAnalyser/security/advisories/new)
- **Ecosystem Security:** `security@open-bricks.org` / `security@ellmos.ai`
- **Maintainer:** `support@lukasgeiger.com` / `lukas@open-bricks.org`
- **Response Commitment:** Initial acknowledgement within **48 hours**; triage within **5 business days**.
