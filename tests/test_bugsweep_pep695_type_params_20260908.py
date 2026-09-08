"""Regressionstests: Bugsweep 2026-09-08 — PEP 695 Type-Parameter-Erkennung & Scope-Binding."""
from __future__ import annotations

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import MethodenAnalyser3 as m3  # noqa: E402


@pytest.mark.skipif(sys.version_info < (3, 12), reason="PEP 695 erfordert Python >= 3.12")
def test_generic_function_typevar_not_in_missing_imports():
    """def identity[T](val: T) -> T darf T nicht als fehlenden Import melden."""
    code = """def identity[T](val: T) -> T:
    return val

res = identity(42)
"""
    result = m3.analyze_source(code, "test_generic_func.py")
    assert "T" not in result.missing_imports, (
        f"T wurde fälschlich als missing_import gemeldet: {result.missing_imports}"
    )
    assert not result.missing_imports
    assert not m3._file_has_findings(result)


@pytest.mark.skipif(sys.version_info < (3, 12), reason="PEP 695 erfordert Python >= 3.12")
def test_generic_function_multiple_type_params():
    """Mehrere Typ-Parameter [K, V] dürfen nicht als missing_imports gemeldet werden."""
    code = """def map_items[K, V](keys: list[K], values: list[V]) -> dict[K, V]:
    return dict(zip(keys, values))

d = map_items(["a"], [1])
"""
    result = m3.analyze_source(code, "test_multi_params.py")
    assert "K" not in result.missing_imports
    assert "V" not in result.missing_imports
    assert not result.missing_imports
    assert not m3._file_has_findings(result)


@pytest.mark.skipif(sys.version_info < (3, 12), reason="PEP 695 erfordert Python >= 3.12")
def test_generic_class_type_params():
    """class Container[T] darf T in Annotationen nicht als missing_import melden."""
    code = """class Container[T]:
    def __init__(self, value: T) -> None:
        self.value: T = value

    def get_value(self) -> T:
        return self.value
"""
    result = m3.analyze_source(code, "test_generic_class.py")
    assert "T" not in result.missing_imports
    assert not result.missing_imports


@pytest.mark.skipif(sys.version_info < (3, 12), reason="PEP 695 erfordert Python >= 3.12")
def test_typevar_tuple_and_paramspec_scope():
    """TypeVarTuple [*Ts] und ParamSpec [**P] dürfen nicht in missing_imports landen."""
    code = """def execute[**P, R](func, *args: P.args, **kwargs: P.kwargs) -> R:
    return func(*args, **kwargs)

def pack[*Ts](*items: *Ts) -> tuple[*Ts]:
    return items
"""
    result = m3.analyze_source(code, "test_paramspec_tuple.py")
    assert "P" not in result.missing_imports
    assert "R" not in result.missing_imports
    assert "Ts" not in result.missing_imports
    assert not result.missing_imports


@pytest.mark.skipif(sys.version_info < (3, 12), reason="PEP 695 erfordert Python >= 3.12")
def test_generic_type_alias_not_in_missing_imports():
    """type Pair[T] = tuple[T, T] darf T nicht als missing_import melden."""
    code = """type Pair[T] = tuple[T, T]
"""
    result = m3.analyze_source(code, "test_generic_alias.py")
    assert "T" not in result.missing_imports
    assert not result.missing_imports


@pytest.mark.skipif(sys.version_info < (3, 12), reason="PEP 695 erfordert Python >= 3.12")
def test_typevar_bound_extracted_into_typehints():
    """TypeVar-Bounds wie [T: int] müssen in result.typehints erfasst werden."""
    code = """def clamp[T: int](val: T, min_val: T, max_val: T) -> T:
    return max(min_val, min(val, max_val))
"""
    result = m3.analyze_source(code, "test_bound_hint.py")
    assert "T" in result.typehints
    assert "int" in result.typehints
    assert "T" not in result.missing_imports
    assert not result.missing_imports
