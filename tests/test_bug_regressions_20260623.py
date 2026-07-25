# -*- coding: utf-8 -*-
"""Regressionstests Bugsweep 2026-06-23 (Desktop, /bugsweep-Loop Run 8/15).

BS-1: Auto-Fix loeschte Imports, die nur in __all__-Strings oder String-/Forward-Ref-
      Annotationen referenziert sind (AST-Name-Analyse erfasst diese nicht) -> kaputte Datei.
BS-2: translator.t() crashte (AttributeError) bei Nicht-dict-Werten in translations.json.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import MethodenAnalyser3 as m3  # noqa: E402
import translator as tl  # noqa: E402


def test_all_referenced_import_not_reported_unused():
    r = m3.analyze_source('from foo import Foo\n__all__ = ["Foo"]\n', "t.py")
    assert "Foo" not in r.unused_imports


def test_forward_ref_import_not_reported_unused():
    r = m3.analyze_source('from bar import Bar\ndef f() -> "Bar":\n    return None\n', "t.py")
    assert "Bar" not in r.unused_imports


def test_genuinely_unused_import_still_detected():
    # Kontrolltest: der Fix darf echte ungenutzte Imports weiter melden.
    r = m3.analyze_source('import os\nx = 1\n', "t.py")
    assert "os" in r.unused_imports


def test_translator_t_non_dict_value_no_crash():
    ts = tl.TranslationSystem('de')
    ts.translations = {"_meta": "irgendein String"}
    assert ts.t("_meta") == "_meta"  # vor dem Fix: AttributeError
