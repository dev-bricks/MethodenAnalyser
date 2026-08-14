"""Regressionstests: Bugsweep 2026-08-14 — AST-Attribut-Ketten & Typen-Introspektion."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import MethodenAnalyser3 as m3


def test_concurrent_futures_threadpoolexecutor_not_in_missing_defs():
    """Multi-Level-Aufruf concurrent.futures.ThreadPoolExecutor darf kein missing_def sein."""
    code = """import concurrent.futures

def run_pool():
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        return executor.submit(lambda: 42)
"""
    result = m3.analyze_source(code, "test_concurrent.py")
    assert "ThreadPoolExecutor" not in result.missing_defs, (
        f"ThreadPoolExecutor wurde fälschlich als missing_def gemeldet: {result.missing_defs}"
    )


def test_asyncio_to_thread_not_in_missing_defs():
    """asyncio.to_thread darf bei import asyncio nicht als fehlende Definition gemeldet werden."""
    code = """import asyncio

async def run_async_task(func):
    return await asyncio.to_thread(func)
"""
    result = m3.analyze_source(code, "test_asyncio.py")
    assert "to_thread" not in result.missing_defs, (
        f"to_thread wurde fälschlich als missing_def gemeldet: {result.missing_defs}"
    )


def test_urllib_request_build_opener_not_in_missing_defs():
    """urllib.request.build_opener darf bei import urllib.request nicht als missing_def gemeldet werden."""
    code = """import urllib.request

def build_http_client():
    opener = urllib.request.build_opener()
    return opener
"""
    result = m3.analyze_source(code, "test_urllib.py")
    assert "build_opener" not in result.missing_defs, (
        f"build_opener wurde fälschlich als missing_def gemeldet: {result.missing_defs}"
    )


def test_nested_typehints_extracted_and_filtered():
    """Verschachtelte TypeHints wie List[CustomModel] oder Optional[ResultHandler] werden erkannt."""
    code = """from typing import List, Optional

class CustomModel:
    pass

def process_items(items: List[CustomModel]) -> Optional[CustomModel]:
    return items[0] if items else None
"""
    result = m3.analyze_source(code, "test_types.py")
    assert "CustomModel" in result.typehints
    assert "List" in result.typehints
    assert "Optional" in result.typehints
    assert "CustomModel" not in result.missing_defs


def test_genuinely_missing_function_still_reported():
    """Echte fehlende Definitionen (wie berechne_eigenen_wert) müssen weiterhin gemeldet werden."""
    code = """def main():
    result = berechne_eigenen_wert(10, 20)
    return result
"""
    result = m3.analyze_source(code, "test_missing.py")
    assert "berechne_eigenen_wert" in result.missing_defs, (
        f"berechne_eigenen_wert muss in missing_defs enthalten sein, war: {result.missing_defs}"
    )


def test_aliased_submodule_attribute_access():
    """import concurrent.futures as cf; cf.ThreadPoolExecutor() auflösen."""
    code = """import concurrent.futures as cf

def run_pool():
    return cf.ThreadPoolExecutor()
"""
    result = m3.analyze_source(code, "test_alias.py")
    assert "ThreadPoolExecutor" not in result.missing_defs
