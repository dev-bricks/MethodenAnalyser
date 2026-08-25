"""Tests for translator.py (P-006 TranslationSystem).

Verifies multi-tier fallback (target_lang -> en -> de -> key), supported languages,
robust path handling, corrupt file recovery, dynamic translations, and scanner capabilities.
"""
from __future__ import annotations

import json

from translator import TranslationSystem


def test_translator_supported_languages():
    tr = TranslationSystem("de")
    assert tr.get_language() == "de"
    langs = tr.get_supported_languages()
    assert "de" in langs
    assert "en" in langs
    assert "es" in langs
    assert "zh" in langs
    assert "ja" in langs
    assert "ru" in langs

    assert tr.is_supported_language("es") is True
    assert tr.is_supported_language("fr") is False

    assert tr.set_language("es") is True
    assert tr.get_language() == "es"
    assert tr.set_language("unknown") is False
    assert tr.get_language() == "es"


def test_translator_multitier_fallback(tmp_path):
    # Setup a custom translations.json
    locales_dir = tmp_path / "locales"
    locales_dir.mkdir(parents=True)
    custom_trans = {
        "full_key": {
            "de": "Vollständig Deutsch",
            "en": "Fully English",
            "es": "Completamente Español",
            "zh": "完整中文",
            "ja": "完全な日本語",
            "ru": "Полный русский"
        },
        "only_de_and_en": {
            "de": "Nur DE und EN",
            "en": "Only DE and EN"
        },
        "only_de": {
            "de": "Nur Deutsch"
        },
        "empty_en": {
            "de": "Deutscher Text",
            "en": "   "
        }
    }
    (locales_dir / "translations.json").write_text(json.dumps(custom_trans), encoding="utf-8")

    tr = TranslationSystem("es", app_dir=tmp_path)

    # 1. Full key in ES -> gives ES
    assert tr.t("full_key") == "Completamente Español"

    # 2. ES missing, falls back to EN
    assert tr.t("only_de_and_en") == "Only DE and EN"

    # 3. ES and EN missing, falls back to DE
    assert tr.t("only_de") == "Nur Deutsch"

    # 4. EN is whitespace, falls back to DE
    assert tr.t("empty_en") == "Deutscher Text"

    # 5. Non-existent key -> returns key itself
    assert tr.t("completely_unknown_key") == "completely_unknown_key"


def test_translator_corrupt_and_missing_file(tmp_path):
    # Non-existent file
    tr_missing = TranslationSystem("en", app_dir=tmp_path / "nonexistent")
    assert tr_missing.t("test_key") == "test_key"

    # Corrupt JSON file
    locales_dir = tmp_path / "locales"
    locales_dir.mkdir(parents=True)
    (locales_dir / "translations.json").write_text("{ invalid json !!", encoding="utf-8")

    tr_corrupt = TranslationSystem("en", app_dir=tmp_path)
    assert tr_corrupt.t("test_key") == "test_key"


def test_translator_add_translation_and_scan(tmp_path):
    tr = TranslationSystem("de", app_dir=tmp_path)
    tr.add_translation("new_action", {"de": "Neue Aktion", "en": "New Action", "es": "Nueva acción"})
    assert tr.t("new_action") == "Neue Aktion"
    tr.set_language("en")
    assert tr.t("new_action") == "New Action"
    tr.set_language("es")
    assert tr.t("new_action") == "Nueva acción"

    missing = tr.get_missing_translations("zh")
    assert "new_action" in missing
