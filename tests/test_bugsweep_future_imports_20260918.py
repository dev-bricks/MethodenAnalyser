# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from MethodenAnalyser3 import _file_has_findings, analyze_source


def test_future_annotations_not_reported_as_unused_import() -> None:
    code = """from __future__ import annotations

def add(a: int, b: int) -> int:
    return a + b

add(1, 2)
"""
    result = analyze_source(code, source_name="test_future.py")
    assert "annotations" not in result.unused_imports
    assert "annotations" not in result.imported_definitions
    assert _file_has_findings(result) is False


def test_future_multiple_features_not_reported_as_unused_import() -> None:
    code = """from __future__ import annotations, division, unicode_literals

x = 10 / 2
"""
    result = analyze_source(code, source_name="test_future_multi.py")
    assert "annotations" not in result.unused_imports
    assert "division" not in result.unused_imports
    assert "unicode_literals" not in result.unused_imports
    assert "annotations" not in result.imported_definitions


def test_future_import_scope_not_in_unused_global() -> None:
    code = """from __future__ import annotations

def greet() -> str:
    return "hello"
"""
    result = analyze_source(code, source_name="test_scope.py")
    assert "annotations" not in result.import_scopes.get("unused_global", [])


def test_genuinely_unused_import_alongside_future_import_still_detected() -> None:
    code = """from __future__ import annotations
import os

def greet() -> str:
    return "hello"
"""
    result = analyze_source(code, source_name="test_real_unused.py")
    assert "annotations" not in result.unused_imports
    assert "os" in result.unused_imports
    assert _file_has_findings(result) is True
