"""Regressionstests: Bugsweep 2026-06-27 — GUI/tkinter/Threading/Export-Lens."""
from __future__ import annotations

import inspect
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import MethodenAnalyser3  # noqa: E402


# ---------------------------------------------------------------------------
# Bug #BS27-1: run_project_analysis() rief .update() statt .update_idletasks()
#   → User-Events (Button-Klicks) wurden mitten in der Analyse verarbeitet,
#     was zu re-entrantem Aufruf und Korrumpierung des globalen State führte.
# ---------------------------------------------------------------------------

def test_run_project_analysis_no_bare_update_call():
    """run_project_analysis() darf .update() nicht mehr aufrufen (Re-entranz-Schutz)."""
    source = inspect.getsource(MethodenAnalyser3.run_project_analysis)
    # .update() ohne idletasks darf nicht mehr vorkommen
    bare_updates = re.findall(r'\.update\s*\(\s*\)', source)
    assert bare_updates == [], (
        f"run_project_analysis() enthält noch .update()-Aufruf(e): {bare_updates}. "
        "Muss .update_idletasks() verwenden (verarbeitet nur Render-Jobs, keine User-Events)."
    )


def test_run_project_analysis_uses_update_idletasks():
    """run_project_analysis() muss .update_idletasks() aufrufen."""
    source = inspect.getsource(MethodenAnalyser3.run_project_analysis)
    assert '.update_idletasks()' in source, (
        "run_project_analysis() muss .update_idletasks() für GUI-Refreshes verwenden."
    )


# ---------------------------------------------------------------------------
# Bug #BS27-2: analyze_project() zählte total_lines für latin-1-Dateien als 0
#   → UnicodeDecodeError wurde einfach ignoriert statt auf latin-1 zu fallen.
# ---------------------------------------------------------------------------

def test_analyze_project_counts_latin1_file_lines():
    """total_lines muss > 0 sein wenn das Projekt nur latin-1-kodierte .py-Dateien enthält."""
    latin1_content = "# Kommentar mit Ümlauts und Sonderzeichen\ndef foo():\n    pass\n"
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "latin1_module.py")
        with open(filepath, 'w', encoding='latin-1') as f:
            f.write(latin1_content)

        result = MethodenAnalyser3.analyze_project(tmpdir)

    assert result.total_lines > 0, (
        f"total_lines={result.total_lines} — latin-1-kodierte .py-Dateien müssen gezählt werden."
    )
    assert result.total_lines == 3, (
        f"Erwartet 3 Zeilen, aber {result.total_lines} gezählt."
    )


def test_analyze_project_counts_utf8_file_lines():
    """Kontrolltest: total_lines für normale UTF-8-Dateien bleibt korrekt."""
    utf8_content = "# UTF-8 Kommentar\ndef bar():\n    return 42\n"
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "utf8_module.py")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(utf8_content)

        result = MethodenAnalyser3.analyze_project(tmpdir)

    assert result.total_lines == 3, (
        f"Erwartet 3 Zeilen für UTF-8-Datei, aber {result.total_lines} gezählt."
    )


# ---------------------------------------------------------------------------
# Bug #BS27-3: run_analysis() nutzte 📄-Emoji im Widget-Insert
#   → Inkonsistent mit bereits entfernten Emojis in get_summary(); auf
#     manchen älteren Tk 8.6 / Windows-Builds kann non-BMP TclError auslösen.
# ---------------------------------------------------------------------------

def test_run_analysis_no_emoji_in_file_header_insert():
    """run_analysis() darf kein Emoji im Widget-Insert für den Datei-Header verwenden."""
    source = inspect.getsource(MethodenAnalyser3.run_analysis)
    assert '\U0001F4C4' not in source, (  # 📄 U+1F4C4
        "run_analysis() enthält noch das 📄-Emoji im Widget-Insert. "
        "Muss durch ASCII-Tag [DATEI] ersetzt worden sein."
    )


def test_run_analysis_file_header_uses_ascii_tag():
    """run_analysis() muss [DATEI]-Tag statt Emoji im Widget-Insert verwenden."""
    source = inspect.getsource(MethodenAnalyser3.run_analysis)
    assert '[DATEI]' in source, (
        "run_analysis() fehlt [DATEI]-Tag im Widget-Insert (Ersatz für 📄-Emoji)."
    )
