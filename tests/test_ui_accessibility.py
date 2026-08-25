"""Tests für UX & Accessibility in MethodenAnalyser3.

Prüft ToolTip-Klasse, barrierefreie Beschriftungen, dynamische Umschaltung,
Statusleisten-Rückmeldungen und Vollständigkeit der Sprachkataloge mit echten Umlauten.
"""
from __future__ import annotations

import json
import sys
import tkinter as tk
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import MethodenAnalyser3 as m


def _reset_language(lang: str) -> None:
    tr = m.get_translator()
    if tr is not None:
        tr.set_language(lang)


def test_translations_catalog_completeness():
    """Prüft, dass alle Translation-Keys für alle 6 Sprachen (DE, EN, ES, ZH, JA, RU) vorhanden und nicht leer sind."""
    catalog_file = ROOT / "locales" / "translations.json"
    assert catalog_file.exists(), "locales/translations.json muss existieren"
    data = json.loads(catalog_file.read_text(encoding="utf-8"))
    
    required_keys = [
        "app_title", "btn_analyze_file", "btn_info", "btn_autofix", "btn_analyze_project",
        "tooltip_analyze_file", "tooltip_info", "tooltip_autofix", "tooltip_analyze_project",
        "shortcut_hint", "menu_language", "status_ready", "status_analyzing_file",
        "status_analyzing_project", "status_analysis_done", "status_autofix_done",
        "status_no_unused_imports", "dialog_select_file", "dialog_select_project",
        "dialog_no_file_title", "dialog_no_file_msg", "dialog_no_unused_title",
        "dialog_no_unused_msg", "dialog_autofix_title", "welcome_body", "info_body",
        "lang_switched_msg"
    ]
    
    for key in required_keys:
        assert key in data, f"Key '{key}' fehlt im Translations-Katalog"
        for lang in ("de", "en", "es", "zh", "ja", "ru"):
            assert lang in data[key] and data[key][lang].strip(), f"'{lang}'-Übersetzung für '{key}' fehlt oder ist leer"


def test_german_typography_and_umlauts():
    """Prüft, dass deutsche Texte echte Umlaute (ä, ö, ü, ß) und keine ASCII-Ersatzformen verwenden."""
    catalog_file = ROOT / "locales" / "translations.json"
    data = json.loads(catalog_file.read_text(encoding="utf-8"))
    
    # Prüfe gezielt Texte mit Umlauten
    assert "Öffnet" in data["tooltip_analyze_file"]["de"]
    assert "Funktionsübersicht" in data["tooltip_info"]["de"]
    assert "auswählen" in data["dialog_select_file"]["de"]
    assert "auswählen" in data["dialog_select_project"]["de"]
    assert "bestätigen" in data["dialog_autofix_title"]["de"]


def test_tooltip_lifecycle():
    """Prüft die Erstellung, Anzeige, Textaktualisierung und das Schließen des ToolTips."""
    root = tk.Tk()
    root.withdraw()
    try:
        btn = tk.Button(root, text="Test")
        btn.pack()
        tip = m.ToolTip(btn, text="Initialer Hinweis")
        assert tip.text == "Initialer Hinweis"
        assert tip.tip_window is None
        
        # Tip anzeigen
        tip.show_tip()
        assert tip.tip_window is not None
        assert tip.tip_window.winfo_exists()
        
        # Text dynamisch aktualisieren
        tip.set_text("Neuer barrierefreier Hinweis")
        assert tip.text == "Neuer barrierefreier Hinweis"
        
        # Tip verstecken
        tip.hide_tip()
        assert tip.tip_window is None
    finally:
        root.destroy()


def test_dynamic_retranslation_of_tooltips_and_status():
    """Prüft, dass Tooltips und Statusleisten-Texte bei Sprachwechsel live übersetzt werden."""
    _reset_language("de")
    assert m._t("status_ready") == "Bereit"
    assert m._t("tooltip_analyze_file").startswith("Öffnet eine Python-Datei")
    
    _reset_language("en")
    assert m._t("status_ready") == "Ready"
    assert m._t("tooltip_analyze_file").startswith("Opens a Python file")
    
    _reset_language("de")
