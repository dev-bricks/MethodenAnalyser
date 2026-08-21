"""Regressionstests: Bugsweep 2026-08-21 — Import-Scopes & From-Import / Alias / Relative-Import-Präzision."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import MethodenAnalyser3 as m3  # noqa: E402


def test_from_module_import_used_not_in_unused_global():
    """from math import sqrt darf bei Verwendung von sqrt() nicht als unused_global gemeldet werden."""
    code = """from math import sqrt

def calc(x):
    return sqrt(x)
"""
    result = m3.analyze_source(code, "test_from_import.py")
    assert "math" not in result.import_scopes.get("unused_global", []), (
        f"math wurde fälschlich in unused_global gemeldet: {result.import_scopes}"
    )
    assert "sqrt" not in result.import_scopes.get("unused_global", []), (
        f"sqrt wurde fälschlich in unused_global gemeldet: {result.import_scopes}"
    )
    assert result.unused_imports == []


def test_from_module_import_unused_is_in_unused_global():
    """from math import sin, cos bei nur sin-Nutzung meldet cos in unused_global und unused_imports."""
    code = """from math import sin, cos

def calc(x):
    return sin(x)
"""
    result = m3.analyze_source(code, "test_unused_from.py")
    assert "cos" in result.import_scopes.get("unused_global", [])
    assert "sin" not in result.import_scopes.get("unused_global", [])
    assert result.unused_imports == ["cos"]


def test_aliased_import_scope_tracking():
    """import os.path as osp darf bei Verwendung von osp nicht als unused_global gemeldet werden."""
    code = """import os.path as osp

def check(path):
    return osp.exists(path)
"""
    result = m3.analyze_source(code, "test_alias_scope.py")
    assert "os" not in result.import_scopes.get("unused_global", [])
    assert "osp" not in result.import_scopes.get("unused_global", [])
    assert result.unused_imports == []


def test_relative_imports_scope_tracking():
    """from . import sibling und from ..utils import helper werden korrekt im Scope erfasst."""
    code = """from . import sibling
from ..utils import helper

def run():
    sibling.do_thing()
    helper.do_other()
"""
    result = m3.analyze_source(code, "test_rel_import.py")
    assert "utils" not in result.import_scopes.get("unused_global", [])
    assert "sibling" not in result.import_scopes.get("unused_global", [])
    assert "helper" not in result.import_scopes.get("unused_global", [])
    assert result.unused_imports == []


def test_local_import_redundant_and_multi_local_precision():
    """Prüft mehrfach lokale und redundante lokale Imports mit from-import Syntax."""
    code = """from math import sqrt

def func_a():
    from math import sqrt
    return sqrt(4)

def func_b():
    from math import ceil
    return ceil(4.2)

def func_c():
    from math import ceil
    return ceil(5.5)
"""
    result = m3.analyze_source(code, "test_scopes.py")
    assert "sqrt" in result.import_scopes.get("redundant_local", [])
    assert "ceil" in result.import_scopes.get("multi_local", [])
