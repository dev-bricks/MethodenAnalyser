"""Regressionstests: Welle-1 U1 — sichtbarer DE/EN-Sprachschalter.

Prueft die Uebersetzungslogik, die Persistenz der Spracheinstellung und den
isinstance-Guard des TranslationSystem (keine GUI noetig, alles headless).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import MethodenAnalyser3 as m  # noqa: E402
from translator import TranslationSystem  # noqa: E402


def _reset_language(lang: str) -> None:
    tr = m.get_translator()
    if tr is not None:
        tr.set_language(lang)


def test_translator_available_with_both_languages():
    tr = m.get_translator()
    assert tr is not None, "TranslationSystem sollte importierbar/verfuegbar sein"
    for key in ("btn_analyze_file", "btn_analyze_project", "shortcut_hint",
                "welcome_body", "info_body"):
        assert m._t(key), f"Uebersetzung fuer {key} darf nicht leer sein"


def test_button_labels_switch_language():
    _reset_language("de")
    assert m._t("btn_analyze_file") == "📂 Datei analysieren"
    assert m._t("btn_analyze_project") == "Projekt analysieren"
    _reset_language("en")
    assert m._t("btn_analyze_file") == "📂 Analyze File"
    assert m._t("btn_analyze_project") == "Analyze Project"
    _reset_language("de")


def test_shortcut_hint_is_translated():
    _reset_language("en")
    assert "Keyboard:" in m._get_keyboard_shortcut_hint()
    _reset_language("de")
    assert "Tastatur:" in m._get_keyboard_shortcut_hint()


def test_welcome_text_substitutes_shortcut_and_switches():
    _reset_language("de")
    text_de = m._build_welcome_text()
    assert "{shortcut}" not in text_de
    assert "Tastatur:" in text_de
    assert text_de.startswith(m._WELCOME_HEADS[0])
    _reset_language("en")
    text_en = m._build_welcome_text()
    assert text_en.startswith(m._WELCOME_HEADS[1])
    assert "Keyboard:" in text_en
    _reset_language("de")


def test_config_language_roundtrip(tmp_path, monkeypatch):
    cfg_dir = tmp_path / "cfg"
    monkeypatch.setattr(m, "_config_dir", lambda: cfg_dir)
    # Nichts gespeichert -> Default
    assert m.get_saved_language() == m.DEFAULT_LANGUAGE
    # Speichern + erneut lesen
    assert m.set_saved_language("en") is True
    assert (cfg_dir / "config.json").exists()
    assert m.get_saved_language() == "en"
    data = json.loads((cfg_dir / "config.json").read_text(encoding="utf-8"))
    assert data["language"] == "en"
    # Ungueltige Sprache wird abgelehnt, alter Wert bleibt
    assert m.set_saved_language("fr") is False
    assert m.get_saved_language() == "en"


def test_unknown_saved_language_falls_back_to_default(tmp_path, monkeypatch):
    cfg_dir = tmp_path / "cfg2"
    cfg_dir.mkdir()
    (cfg_dir / "config.json").write_text('{"language": "xx"}', encoding="utf-8")
    monkeypatch.setattr(m, "_config_dir", lambda: cfg_dir)
    assert m.get_saved_language() == m.DEFAULT_LANGUAGE


def test_corrupt_config_is_tolerated(tmp_path, monkeypatch):
    cfg_dir = tmp_path / "cfg3"
    cfg_dir.mkdir()
    (cfg_dir / "config.json").write_text("{ this is not valid json", encoding="utf-8")
    monkeypatch.setattr(m, "_config_dir", lambda: cfg_dir)
    # Darf nicht crashen, faellt auf Default zurueck
    assert m.get_saved_language() == m.DEFAULT_LANGUAGE


def test_translator_guard_handles_corrupt_entry():
    tr = TranslationSystem("de")
    tr.translations["__broken__"] = "not-a-dict"
    # isinstance-Guard: darf nicht mit AttributeError crashen
    assert tr.t("__broken__") == "__broken__"
