"""Tests for advanced AST features in MethodenAnalyser3.

Verifies:
- Python 3.10+ Pattern Matching bindings (MatchAs, MatchStar, MatchMapping)
- Global and Nonlocal variable declarations
- Relative imports without module names (from . import foo, bar)
- TypeAlias and annotation extraction
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import MethodenAnalyser3 as m3


def test_relative_import_without_module_name():
    code = """
from . import config, utils

def run():
    return config.DEBUG + utils.calc()
"""
    result = m3.analyze_source(code, "<relative_import_test>")
    # config and utils must be recognized as imported modules/definitions
    assert "config" not in result.missing_imports
    assert "utils" not in result.missing_imports
    assert "config" not in result.unused_imports
    assert "utils" not in result.unused_imports


def test_global_and_nonlocal_variable_bindings():
    code = """
counter = 0

def outer():
    x = 10
    def inner():
        nonlocal x
        global counter
        x += 1
        counter += 1
        return x + counter
    return inner()
"""
    result = m3.analyze_source(code, "<global_nonlocal_test>")
    assert "x" not in result.missing_defs
    assert "counter" not in result.missing_defs
    assert "counter" not in result.missing_imports


def test_pattern_matching_bindings():
    code = """
def handle_command(command):
    match command:
        case ["go", direction]:
            return f"going {direction}"
        case ["take", *items]:
            return f"taking {items}"
        case {"action": act, **options}:
            return f"action {act} with {options}"
        case _:
            return "unknown"
"""
    result = m3.analyze_source(code, "<match_pattern_test>")
    # direction, items, act, options must not be marked as missing definitions or missing imports
    assert "direction" not in result.missing_defs
    assert "direction" not in result.missing_imports
    assert "items" not in result.missing_defs
    assert "items" not in result.missing_imports
    assert "act" not in result.missing_defs
    assert "act" not in result.missing_imports
    assert "options" not in result.missing_defs
    assert "options" not in result.missing_imports


def test_type_alias_extraction():
    code = """
from typing import List, Dict, Union

type UserId = int
type UserList = List[UserId]
type ConfigMap = Dict[str, Union[int, str]]

def process_users(users: UserList) -> ConfigMap:
    return {"count": len(users)}
"""
    result = m3.analyze_source(code, "<type_alias_test>")
    # List, Dict, Union should be considered used through annotations/type aliases
    assert "List" not in result.unused_imports
    assert "Dict" not in result.unused_imports
    assert "Union" not in result.unused_imports
