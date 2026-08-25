"""Regressionstests: Multi-Language-Support (DE, EN, ES, ZH, JA, RU).

Prüft die Übersetzungslosgik, die Persistenz der Spracheinstellung,
die Mehrsprachigkeit aller 6 Sprachen und den isinstance-Guard des TranslationSystem.
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


def test_translator_available_with_all_languages():
    tr = m.get_translator()
    assert tr is not None, "TranslationSystem sollte importierbar/verfügbar sein"
    for key in ("btn_analyze_file", "btn_analyze_project", "shortcut_hint",
                "welcome_body", "info_body"):
        for lang in ("de", "en", "es", "zh", "ja", "ru"):
            _reset_language(lang)
            assert m._t(key), f"Übersetzung für {key} ({lang}) darf nicht leer sein"
    _reset_language("de")


def test_button_labels_switch_all_languages():
    expected = {
        "de": ("📂 Datei analysieren", "Projekt analysieren"),
        "en": ("📂 Analyze File", "Analyze Project"),
        "es": ("📂 Analizar archivo", "Analizar proyecto"),
        "zh": ("📂 分析文件", "分析项目"),
        "ja": ("📂 ファイルを分析", "プロジェクトを分析"),
        "ru": ("📂 Анализировать файл", "Анализировать проект"),
    }
    for lang, (btn_file, btn_proj) in expected.items():
        _reset_language(lang)
        assert m._t("btn_analyze_file") == btn_file
        assert m._t("btn_analyze_project") == btn_proj
    _reset_language("de")


def test_shortcut_hint_is_translated():
    _reset_language("en")
    assert "Keyboard:" in m._get_keyboard_shortcut_hint()
    _reset_language("de")
    assert "Tastatur:" in m._get_keyboard_shortcut_hint()
    _reset_language("es")
    assert "Teclado:" in m._get_keyboard_shortcut_hint()
    _reset_language("zh")
    assert "快捷键:" in m._get_keyboard_shortcut_hint()
    _reset_language("ja")
    assert "キーボード:" in m._get_keyboard_shortcut_hint()
    _reset_language("ru")
    assert "Горячие клавиши:" in m._get_keyboard_shortcut_hint()
    _reset_language("de")


def test_welcome_text_substitutes_shortcut_and_switches():
    for idx, lang in enumerate(("de", "en", "es", "zh", "ja", "ru")):
        _reset_language(lang)
        text = m._build_welcome_text()
        assert "{shortcut}" not in text
        assert text.startswith(m._WELCOME_HEADS[idx])
    _reset_language("de")


def test_config_language_roundtrip(tmp_path, monkeypatch):
    cfg_dir = tmp_path / "cfg"
    monkeypatch.setattr(m, "_config_dir", lambda: cfg_dir)
    # Nichts gespeichert -> Default
    assert m.get_saved_language() == m.DEFAULT_LANGUAGE
    # Speichern + erneut lesen
    for lang in ("en", "es", "zh", "ja", "ru", "de"):
        assert m.set_saved_language(lang) is True
        assert (cfg_dir / "config.json").exists()
        assert m.get_saved_language() == lang
        data = json.loads((cfg_dir / "config.json").read_text(encoding="utf-8"))
        assert data["language"] == lang

    # Ungültige Sprache wird abgelehnt, alter Wert bleibt
    assert m.set_saved_language("invalid_lang") is False
    assert m.get_saved_language() == "de"


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
    # Darf nicht crashen, fällt auf Default zurück
    assert m.get_saved_language() == m.DEFAULT_LANGUAGE


def test_translator_guard_handles_corrupt_entry():
    tr = TranslationSystem("de")
    tr.translations["__broken__"] = "not-a-dict"
    # isinstance-Guard: darf nicht mit AttributeError crashen
    assert tr.t("__broken__") == "__broken__"
