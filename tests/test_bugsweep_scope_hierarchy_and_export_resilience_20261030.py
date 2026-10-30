"""
Regressionstests: Bugsweep 2026-10-30 — Scope-Hierarchie, Multi-Local Kollision & Exportpfad-Resilienz.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import MethodenAnalyser3 as m3


def test_multi_local_distinct_classes_same_method_name():
    """
    Methoden mit demselben Namen in unterschiedlichen Klassen (z.B. Worker1.run und Worker2.run)
    dürfen nicht im selben Scope-Schlüssel kollidieren.
    Wenn math in beiden lokal importiert wird, MUSS math in multi_local erkannt werden.
    """
    code = """
class Worker1:
    def run(self):
        import math
        return math.sqrt(4)

class Worker2:
    def run(self):
        import math
        return math.ceil(5.5)
"""
    result = m3.analyze_source(code, "test_multi_class.py")
    multi_local = result.import_scopes.get("multi_local", [])
    assert "math" in multi_local, (
        f"math wurde nicht in multi_local erkannt (Kollision auf 'run'): {result.import_scopes}"
    )


def test_distinct_methods_in_different_classes_do_not_mix_imports():
    """
    Wenn Worker1.run 'json' und Worker2.run 'sqlite3' importiert, dürfen diese
    nicht in einem gemeinsamen Methoden-Scope vermengt werden.
    """
    code = """
class Worker1:
    def run(self):
        import json
        return json.dumps({})

class Worker2:
    def run(self):
        import sqlite3
        return sqlite3.connect(":memory:")
"""
    result = m3.analyze_source(code, "test_distinct_imports.py")
    multi_local = result.import_scopes.get("multi_local", [])
    assert "json" not in multi_local
    assert "sqlite3" not in multi_local


def test_nested_function_scopes_qualified_names():
    """
    Geschachtelte Funktionen mit gleichem Namen in verschiedenen Funktionen
    (outer1.helper vs outer2.helper) werden als getrennte Scopes geführt.
    """
    code = """
def outer1():
    def helper():
        import re
        return re.compile(r"abc")
    return helper()

def outer2():
    def helper():
        import re
        return re.compile(r"xyz")
    return helper()
"""
    result = m3.analyze_source(code, "test_nested_helper.py")
    multi_local = result.import_scopes.get("multi_local", [])
    assert "re" in multi_local, (
        f"re wurde nicht in multi_local für geschachtelte helper() erkannt: {result.import_scopes}"
    )


def test_write_json_report_to_existing_directory_resolves_default_filename():
    """
    Wenn write_json_report ein existierendes Verzeichnis als Ziel erhält,
    darf kein PermissionError ausgelöst werden; der Report muss als
    <dir>/methodenanalyser-report-v1.json gespeichert werden.
    """
    with tempfile.TemporaryDirectory() as td:
        dir_target = os.path.join(td, "export_dir")
        os.makedirs(dir_target, exist_ok=True)
        report_data = {
            "schema_version": m3.JSON_SCHEMA_VERSION,
            "tool_version": m3.TOOL_VERSION,
            "source_kind": "snippet",
            "summary": {},
        }
        written = m3.write_json_report(report_data, dir_target)
        assert os.path.isfile(written)
        assert os.path.basename(written) == m3.DEFAULT_JSON_REPORT_NAME
        assert Path(written).parent.resolve() == Path(dir_target).resolve()


def test_write_json_report_trailing_slash_creates_directory():
    """
    Ein Pfad mit abschließendem Schrägstrich (z.B. 'sub/reports/') signalisiert
    ein Verzeichnisziel und muss zu <path>/methodenanalyser-report-v1.json aufgelöst werden.
    """
    with tempfile.TemporaryDirectory() as td:
        slash_target = os.path.join(td, "sub_reports") + "/"
        report_data = {
            "schema_version": m3.JSON_SCHEMA_VERSION,
            "tool_version": m3.TOOL_VERSION,
            "source_kind": "snippet",
            "summary": {},
        }
        written = m3.write_json_report(report_data, slash_target)
        assert os.path.isfile(written)
        assert os.path.basename(written) == m3.DEFAULT_JSON_REPORT_NAME


def test_manage_translations_check_outside_repo_cwd():
    """
    manage_translations.py --check muss auch bei Ausführung aus einem fremden
    Arbeitsverzeichnis (CWD) ohne Fehler die translations.json finden und 0 zurückgeben.
    """
    manage_py = ROOT / "manage_translations.py"
    with tempfile.TemporaryDirectory() as foreign_cwd:
        res = subprocess.run(
            [sys.executable, str(manage_py), "--check"],
            cwd=foreign_cwd,
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0, f"Fehler bei fremdem CWD: {res.stdout}\n{res.stderr}"
