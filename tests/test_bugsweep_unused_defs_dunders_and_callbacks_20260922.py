"""Regression tests for Bugsweep 2026-09-22: False positive detection in unused_defs.

Bugsweep focus: Definitions-Nutzungsanalyse (unused_defs: Dunder-Methoden,
Callback-Referenzen, TypeHints, __all__ und Framework-Hooks).

Verifies that:
1. Dunder/magic methods (__init__, __str__, __enter__, etc.) are not reported in unused_defs.
2. Functions and classes exported via __all__ are not reported in unused_defs.
3. Functions passed as callbacks (command=my_cb) or stored in dicts/lists are not in unused_defs.
4. Base classes inherited by child classes and functions used as decorators are not in unused_defs.
5. Classes and type aliases used in type annotations are not in unused_defs.
6. Genuinely unused definitions are still reported in unused_defs.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from MethodenAnalyser3 import _file_has_findings, analyze_source


def test_dunder_methods_not_reported_as_unused_defs() -> None:
    """Magic/dunder methods called via Python protocol should not be in unused_defs."""
    code = """class Worker:
    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def run(self) -> str:
        return self.name

w = Worker("job")
w.run()
"""
    result = analyze_source(code, source_name="test_dunder.py")
    assert "__init__" not in result.unused_defs
    assert "__str__" not in result.unused_defs
    assert "__enter__" not in result.unused_defs
    assert "__exit__" not in result.unused_defs
    assert result.unused_defs == []
    assert _file_has_findings(result) is False


def test_all_exported_definitions_not_reported_as_unused_defs() -> None:
    """Public functions and classes exported via __all__ should not be in unused_defs."""
    code = """__all__ = ["PublicService", "calculate_sum"]

class PublicService:
    def process(self):
        pass

def calculate_sum(a: int, b: int) -> int:
    return a + b
"""
    result = analyze_source(code, source_name="test_all_export.py")
    assert "PublicService" not in result.unused_defs
    assert "calculate_sum" not in result.unused_defs
    assert result.unused_defs == []
    assert _file_has_findings(result) is False


def test_callback_and_data_structure_references_not_in_unused_defs() -> None:
    """Functions referenced as callbacks or stored in mappings should not be in unused_defs."""
    code = """def on_click():
    pass

def on_hover():
    pass

def handler_a():
    pass

def handler_b():
    pass

handlers = [handler_a, handler_b]
registry = {"click": on_click, "hover": on_hover}
"""
    result = analyze_source(code, source_name="test_callbacks.py")
    assert "on_click" not in result.unused_defs
    assert "on_hover" not in result.unused_defs
    assert "handler_a" not in result.unused_defs
    assert "handler_b" not in result.unused_defs
    assert result.unused_defs == []


def test_subclass_base_and_decorators_not_in_unused_defs() -> None:
    """Base classes and decorator functions should not be reported in unused_defs."""
    code = """def simple_decorator(func):
    return func

class BaseWorker:
    pass

@simple_decorator
class DerivedWorker(BaseWorker):
    pass

dw = DerivedWorker()
"""
    result = analyze_source(code, source_name="test_inheritance.py")
    assert "BaseWorker" not in result.unused_defs
    assert "simple_decorator" not in result.unused_defs
    assert result.unused_defs == []


def test_type_annotation_definitions_not_in_unused_defs() -> None:
    """Classes and type aliases used in annotations should not be reported in unused_defs."""
    code = """class ContextPayload:
    pass

def handle(payload: ContextPayload) -> None:
    pass

handle(ContextPayload())
"""
    result = analyze_source(code, source_name="test_type_defs.py")
    assert "ContextPayload" not in result.unused_defs
    assert result.unused_defs == []


def test_genuinely_unused_definitions_still_detected() -> None:
    """Genuinely unused functions and classes must still be detected in unused_defs."""
    code = """def genuinely_unused_helper():
    pass

class GenuinelyUnusedClass:
    pass

def active_func():
    pass

active_func()
"""
    result = analyze_source(code, source_name="test_real_unused_defs.py")
    assert "genuinely_unused_helper" in result.unused_defs
    assert "GenuinelyUnusedClass" in result.unused_defs
    assert "active_func" not in result.unused_defs
    assert _file_has_findings(result) is True
