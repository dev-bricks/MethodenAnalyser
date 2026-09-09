# Third-Party Licenses & Dependencies / Drittanbieter-Lizenzen

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
| **pytest** | `>=7.0.0` | Automated test runner & assertions | MIT License | [pytest-dev/pytest](https://github.com/pytest-dev/pytest) |
| **ruff** | `>=0.3.0` | Fast Python linter & code formatter | MIT / Apache 2.0 | [astral-sh/ruff](https://github.com/astral-sh/ruff) |
| **PyInstaller** | `>=6.0.0` | Windows portable EXE compilation (`build_exe.bat`) | GPL-2.0 / Special Exception | [pyinstaller/pyinstaller](https://github.com/pyinstaller/pyinstaller) |

---

## 3. Project License

MethodenAnalyser itself is open-source software licensed under the **MIT License**.

See [LICENSE](LICENSE) for the full text.
