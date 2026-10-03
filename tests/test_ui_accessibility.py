"""Tests für UX & Accessibility in MethodenAnalyser3.

Prüft ToolTip-Klasse, barrierefreie Beschriftungen, dynamische Umschaltung,
Statusleisten-Rückmeldungen und Vollständigkeit der Sprachkataloge mit echten Umlauten.
"""
from __future__ import annotations

import json
import sys
import tkinter as tk
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import MethodenAnalyser3 as m


def _make_tk_root() -> tk.Tk:
    try:
        root = tk.Tk()
        root.withdraw()
        return root
    except (tk.TclError, RuntimeError) as exc:
        pytest.skip(f"Tkinter display/tcl runtime unavailable: {exc}")


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
        "dialog_no_unused_msg", "dialog_partial_unused_title", "dialog_partial_unused_msg",
        "dialog_autofix_title", "welcome_body", "info_body",
        "lang_switched_msg",
        "menu_file", "menu_actions", "menu_help", "menu_analyze_file", "menu_analyze_project",
        "menu_save_report", "menu_exit", "menu_autofix", "menu_select_all", "menu_copy",
        "menu_clear_output", "menu_shortcuts", "menu_about", "dialog_shortcuts_title",
        "dialog_shortcuts_subtitle", "dialog_shortcuts_cat_nav", "dialog_shortcuts_cat_actions",
        "dialog_shortcuts_cat_general", "dialog_shortcuts_a11y_notice", "dialog_btn_close",
        "status_report_saved", "status_output_cleared", "dialog_save_report_title",
        "dialog_filetypes_txt",
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
    assert "Tastaturkürzel" in data["dialog_shortcuts_title"]["de"]
    assert "Übersicht" in data["dialog_shortcuts_subtitle"]["de"]
    assert "Schließen" in data["dialog_btn_close"]["de"]
    assert "Über" in data["menu_about"]["de"]
    assert "auswählen" in data["menu_select_all"]["de"]
    assert "Erfüllt" in data["dialog_shortcuts_a11y_notice"]["de"]
    assert "Unterstützung" in data["dialog_shortcuts_a11y_notice"]["de"]


def test_tooltip_lifecycle():
    """Prüft die Erstellung, Anzeige, Textaktualisierung und das Schließen des ToolTips."""
    root = _make_tk_root()
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
    except tk.TclError as exc:
        pytest.skip(f"Tkinter runtime error during tooltip lifecycle: {exc}")
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


def test_partial_unused_import_dialog_uses_active_language(monkeypatch, tmp_path):
    """Teilweise genutzte Imports dürfen keine fest verdrahtete DE-Meldung zeigen."""
    source = tmp_path / "partial_import.py"
    source.write_text("from package import used, unused\n", encoding="utf-8")
    result = m.AnalysisResult(
        calls=[], defs=[], imported_definitions=[], module_provided_attrs=[],
        missing_defs=[], unused_defs=[], imports=[], used_imports=[],
        unused_imports=["unused"], duplicate_imports=[], missing_imports=[],
    )
    shown: list[tuple[str, str]] = []

    monkeypatch.setattr(m, "_last_analysis_path", str(source))
    monkeypatch.setattr(m, "_last_analysis_result", result)
    monkeypatch.setattr(m.messagebox, "showinfo", lambda title, text: shown.append((title, text)))
    monkeypatch.setattr(m.messagebox, "askyesno", lambda _title, _text: True)
    _reset_language("en")

    m.auto_fix_unused_imports(output_widget=None)

    assert shown == [(m._t("dialog_partial_unused_title"), m._t("dialog_partial_unused_msg"))]
    assert "Partially used imports" in shown[0][1]
    _reset_language("de")


def test_shortcuts_dialog_lifecycle_and_a11y():
    """Prüft den barrierefreien Tastaturkürzel-Dialog inkl. WCAG 2.1 AA / BITV 2.0 Hinweis."""
    _reset_language("de")
    root = _make_tk_root()
    try:
        dlg = m.show_shortcuts_dialog(root)
        assert dlg is not None
        assert dlg.winfo_exists()
        assert m._t("dialog_shortcuts_title") in dlg.title()

        # Inhalte im Dialog prüfen
        shortcuts_text = m._build_shortcuts_text()
        assert m._t("dialog_shortcuts_cat_nav") in shortcuts_text
        assert m._t("dialog_shortcuts_cat_actions") in shortcuts_text
        assert m._t("dialog_shortcuts_cat_general") in shortcuts_text
        assert "Alt+D" in shortcuts_text
        assert "F1" in shortcuts_text

        # Barrierefreiheits-Hinweis
        notice = m._t("dialog_shortcuts_a11y_notice")
        assert "WCAG 2.1 AA" in notice
        assert "BITV 2.0" in notice

        dlg.destroy()
    except tk.TclError as exc:
        pytest.skip(f"Tkinter runtime error during shortcuts dialog lifecycle: {exc}")
    finally:
        root.destroy()


def test_shortcuts_dialog_headless_guard(monkeypatch):
    """Prüft, dass im Headless-Modus kein Fehler geworfen wird und None zurückgegeben wird."""
    monkeypatch.setenv("HEADLESS", "1")
    assert m.show_shortcuts_dialog(None) is None


def test_shortcuts_dialog_multilingual():
    """Prüft die korrekte Übersetzung des Shortcuts-Texts in verschiedenen Sprachen."""
    _reset_language("en")
    en_text = m._build_shortcuts_text()
    assert "Navigation & Analysis" in en_text
    assert "Edit & Actions" in en_text
    assert "Help & Controls" in en_text

    _reset_language("de")
    de_text = m._build_shortcuts_text()
    assert "Navigation & Analyse" in de_text
    assert "Bearbeiten & Aktionen" in de_text
    assert "Hilfe & Steuerung" in de_text


def test_clear_output_view_restores_welcome():
    """Prüft, dass clear_output_view das Widget leert und den Willkommenstext wiederherstellt."""
    root = _make_tk_root()
    try:
        txt = tk.Text(root)
        status = tk.Label(root)
        txt.insert("1.0", "Alte Analyseausgabe...")
        assert "Alte Analyseausgabe..." in txt.get("1.0", "end")

        m.clear_output_view(txt, status)
        assert m._build_welcome_text().strip() in txt.get("1.0", "end")
        assert status.cget("text") == m._t("status_output_cleared")
    except tk.TclError as exc:
        pytest.skip(f"Tkinter runtime error during text widget interaction: {exc}")
    finally:
        root.destroy()


def test_gui_shortcuts_expanded_registration():
    """Prüft, dass alle erweiterten Shortcuts in _register_gui_shortcuts gebunden werden."""
    class FakeRoot:
        def __init__(self) -> None:
            self.bindings: dict[str, Any] = {}

        def bind_all(self, sequence: str, handler: Any) -> None:
            self.bindings[sequence] = handler

    root = FakeRoot()
    calls: list[str] = []

    m._register_gui_shortcuts(
        root,
        analyze_file_cb=lambda: calls.append("file"),
        info_cb=lambda: calls.append("info"),
        auto_fix_cb=lambda: calls.append("autofix"),
        analyze_project_cb=lambda: calls.append("project"),
        shortcuts_cb=lambda: calls.append("shortcuts"),
        save_report_cb=lambda: calls.append("save"),
        clear_output_cb=lambda: calls.append("clear"),
        quit_cb=lambda: calls.append("quit"),
    )

    expected_sequences = [
        "<Alt-d>", "<Alt-D>", "<Alt-p>", "<Alt-P>", "<Alt-f>", "<Alt-F>",
        "<F1>", "<Shift-F1>", "<Control-s>", "<Control-S>",
        "<Control-l>", "<Control-L>", "<Control-q>", "<Control-Q>",
        "<Control-o>", "<Control-O>", "<Control-Shift-O>", "<Control-Shift-o>",
    ]
    for seq in expected_sequences:
        assert seq in root.bindings, f"Shortcut-Sequenz '{seq}' fehlt in bindings"

    assert root.bindings["<F1>"](None) == "break"
    assert "shortcuts" in calls
    assert root.bindings["<Shift-F1>"](None) == "break"
    assert "info" in calls
    assert root.bindings["<Control-s>"](None) == "break"
    assert "save" in calls
    assert root.bindings["<Control-l>"](None) == "break"
    assert "clear" in calls
