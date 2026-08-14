"""Regressionstests: Bugsweep Lauf #9 — translator.py + manage_translations.py."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch, mock_open

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from translator import TranslationSystem  # noqa: E402


# ---------------------------------------------------------------------------
# Bug #9-1: german_hints enthält ASCII-Digraphe und false-positive "ok"
# ---------------------------------------------------------------------------

def test_is_german_does_not_match_english_ok():
    """'ok' darf nicht als deutsch erkannt werden (Bug #9-1)."""
    tr = TranslationSystem()
    assert not tr._is_german("ok"), "'ok' sollte kein Deutsch-Indikator sein"
    assert not tr._is_german("The hook is ok"), "englischer Text mit 'ok' darf nicht matchen"


def test_is_german_does_not_match_oeffnen_digraph():
    """ASCII-Digraph 'oeffnen' soll nicht mehr als Hint gelten (Bug #9-1)."""
    tr = TranslationSystem()
    # "oeffnen" als ASCII-Only-String hat keine Umlaute → soll nicht matchen
    assert not tr._is_german("oeffnen"), "'oeffnen' ohne Umlaut soll nicht als deutsch gelten"


def test_is_german_matches_real_umlaut():
    """Echter Umlaut muss nach wie vor erkannt werden."""
    tr = TranslationSystem()
    assert tr._is_german("Öffnen"), "Öffnen (mit echtem Umlaut) muss als deutsch erkannt werden"
    assert tr._is_german("Schließen"), "Schließen (mit ß) muss als deutsch erkannt werden"
    assert tr._is_german("Einstellungen"), "'einstellungen' im Hint soll matchen"


def test_is_german_does_not_match_pure_english():
    """Rein englischer Text ohne Umlauts-Hints soll nicht matchen."""
    tr = TranslationSystem()
    assert not tr._is_german("Open file"), "englisch 'Open file' soll nicht matchen"
    assert not tr._is_german("Settings"), "englisch 'Settings' soll nicht matchen"


# ---------------------------------------------------------------------------
# Bug #9-2: _save_translations() kein try/except OSError
# ---------------------------------------------------------------------------

def test_save_translations_does_not_raise_on_oserror():
    """_save_translations() darf bei OSError keine Exception nach außen geben (Bug #9-2)."""
    tr = TranslationSystem()
    tr.translations = {"Test": {"de": "Test", "en": "Test"}}
    with patch("builtins.open", mock_open()) as m:
        m.side_effect = OSError("Disk full")
        try:
            tr._save_translations()
        except OSError:
            raise AssertionError("_save_translations() muss OSError intern abfangen")


# ---------------------------------------------------------------------------
# Bug #9-3: manage_translations.py GERMAN_HINTS hat ASCII-Digraphe
# ---------------------------------------------------------------------------

def test_manage_translations_hints_no_digraphs():
    """GERMAN_HINTS in manage_translations darf keine ASCII-Digraphe enthalten (Bug #9-3)."""
    import manage_translations as mt
    for hint in mt.GERMAN_HINTS:
        assert "oe" not in hint or "oe" in {"poem", "poet"}, \
            f"'{hint}' enthält 'oe' — möglicher ASCII-Digraph für 'ö'"
        assert "ae" not in hint, f"'{hint}' enthält 'ae' — möglicher ASCII-Digraph für 'ä'"
        assert "ue" not in hint, f"'{hint}' enthält 'ue' — möglicher ASCII-Digraph für 'ü'"
        assert hint != "ok", "'ok' darf kein Deutsch-Hint sein (false positive)"


# ---------------------------------------------------------------------------
# Bug #9-4: manage_translations JSON-Lesen ohne try/except JSONDecodeError
# ---------------------------------------------------------------------------

def test_manage_translations_survives_corrupt_json(tmp_path):
    """manage_translations muss bei korruptem JSON weiterlaufen (Bug #9-4)."""
    import manage_translations as mt

    trans_dir = tmp_path / "locales"
    trans_dir.mkdir()
    corrupt_file = trans_dir / "translations.json"
    corrupt_file.write_text("{invalid json", encoding="utf-8")

    try:
        mt.manage_translations(str(tmp_path))
    except (json.JSONDecodeError, OSError) as e:
        raise AssertionError(f"manage_translations() darf bei korruptem JSON nicht abstürzen: {e}")


# ---------------------------------------------------------------------------
# Bug #9-5: manage_translations JSON-Schreiben ohne try/except OSError
# ---------------------------------------------------------------------------

def test_manage_translations_survives_write_oserror(tmp_path):
    """manage_translations darf bei Schreib-Fehler nicht abstürzen (Bug #9-5)."""
    import manage_translations as mt

    with patch("builtins.open", mock_open()) as m:
        m.side_effect = OSError("Read-only filesystem")
        try:
            mt.manage_translations(str(tmp_path))
        except OSError:
            raise AssertionError(
                "manage_translations() muss OSError beim Schreiben intern abfangen"
            )


# ---------------------------------------------------------------------------
# Bug #9-6: test_cli.py setUp() verwendete veraltete German-Hints-Liste
# ---------------------------------------------------------------------------

def test_test_cli_translator_hints_no_digraphs():
    """setUp() in TranslatorIsGermanTests darf keine ASCII-Digraphe mehr enthalten (Bug #9-6)."""
    import ast
    import pathlib

    src = (pathlib.Path(__file__).parent / "test_cli.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TranslatorIsGermanTests":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "setUp":
                    for subnode in ast.walk(item):
                        if isinstance(subnode, ast.Constant) and isinstance(subnode.value, str):
                            hint = subnode.value
                            assert "oe" not in hint or hint in {"poem", "poet"}, \
                                f"setUp() enthält veralteten ASCII-Digraph: '{hint}'"
                            assert "ae" not in hint, \
                                f"setUp() enthält veralteten ASCII-Digraph: '{hint}'"
                            assert "ue" not in hint, \
                                f"setUp() enthält veralteten ASCII-Digraph: '{hint}'"
                            assert hint != "ok", \
                                "setUp() enthält false-positive 'ok'"


# ---------------------------------------------------------------------------
# Bug #9-7: subprocess.run() ohne timeout= in test_cli.py-Helpern
# ---------------------------------------------------------------------------

def test_test_cli_subprocess_run_has_timeout():
    """Alle subprocess.run()-Aufrufe in test_cli.py müssen timeout= setzen (Bug #9-7)."""
    import ast
    import pathlib

    src = (pathlib.Path(__file__).parent / "test_cli.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "run"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "subprocess"
        ):
            kwarg_names = {kw.arg for kw in node.keywords}
            assert "timeout" in kwarg_names, (
                f"subprocess.run() in test_cli.py (Zeile {node.lineno}) "
                "fehlt timeout= — hängender Subprozess blockiert den Test-Runner unbegrenzt"
            )


# ---------------------------------------------------------------------------
# Bug #9-8: User-facing Strings in MethodenAnalyser3.py mit ASCII-Digraphen
# ---------------------------------------------------------------------------

def test_main_file_no_digraphs_in_user_strings():
    """ASCII-Digraphe in String-Literalen von MethodenAnalyser3.py verboten (Bug #9-8)."""
    import ast
    import pathlib
    import re

    src = pathlib.Path(__file__).resolve().parents[1] / "MethodenAnalyser3.py"
    text = src.read_text(encoding="utf-8")
    tree = ast.parse(text)

    GERMAN_DIGRAPH_RE = re.compile(
        r"\b(?:koennen|fuer|auswaehlen|auswahlen|oeffnen|schliessen|loeschen|"
        r"zurueck|aendern|groesse|naechst|ueber|enthaelt)\b",
        re.IGNORECASE,
    )

    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            m = GERMAN_DIGRAPH_RE.search(node.value)
            if m:
                violations.append(
                    f"Zeile {node.lineno}: '{m.group()}' in {node.value!r}"
                )

    assert not violations, (
        "ASCII-Digraphe in User-Strings gefunden (Bug #9-8) — "
        "echte Umlaute ä/ö/ü verwenden:\n" + "\n".join(violations)
    )
