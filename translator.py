"""
TranslationSystem - Multi-Language Support für Anwendungen (P-006 Standard)
==========================================================================
Version: 2.0.0
Unterstützt: Standard Tier 1 (DE, EN) und Premium Tier 2 (ES, ZH, JA, RU).
Fallback-Kette: Zielsprache -> en -> de -> Translation-Key

Verwendung:
-----------
from translator import TranslationSystem

translator = TranslationSystem('de')
label.setText(translator.t('btn_analyze_file'))
translator.set_language('es')
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union


class TranslationSystem:
    """Multi-Language Support System v2.0 gem. P-006 Standard."""

    SUPPORTED_LANGUAGES: tuple[str, ...] = ("de", "en", "es", "zh", "ja", "ru")
    DEFAULT_LANGUAGE: str = "de"

    def __init__(self, default_lang: str = "de", app_dir: Optional[Union[str, Path]] = None):
        """
        Initialisiert das Translation-System.

        Args:
            default_lang: Standard-Sprache ('de', 'en', 'es', 'zh', 'ja', 'ru')
            app_dir: Verzeichnis der Anwendung (default: Verzeichnis dieser Datei)
        """
        self.current_lang = default_lang if default_lang in self.SUPPORTED_LANGUAGES else self.DEFAULT_LANGUAGE

        if app_dir is None:
            self.app_dir = Path(__file__).resolve().parent
        else:
            self.app_dir = Path(app_dir).resolve()

        self.translations_file = self.app_dir / "locales" / "translations.json"

        self.string_patterns = [
            re.compile(r'setText\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'setWindowTitle\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'QLabel\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'QPushButton\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'addAction\s*\([^,]*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'addTab\s*\([^,]+,\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'text\s*=\s*"([^"]+)"'),
        ]

        self.german_hints = [
            "datei", "bearbeiten", "ansicht", "hilfe", "speichern",
            "einstellungen", "abbrechen", "nein", "ja",
            "fortsetzen", "laden", "aktualisieren",
            "fehler", "optionen", "anzeigen",
        ]

        self.translations: Dict[str, Any] = {}
        self._load_translations()

    def _load_translations(self) -> None:
        """Lädt Übersetzungen aus der JSON-Datei."""
        if self.translations_file.exists():
            try:
                with open(self.translations_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.translations = data if isinstance(data, dict) else {}
            except Exception:
                self.translations = {}
        else:
            self.translations = {}

    def _save_translations(self) -> None:
        """Speichert Übersetzungen in die JSON-Datei."""
        try:
            self.translations_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.translations_file, "w", encoding="utf-8") as f:
                json.dump(self.translations, f, indent=2, ensure_ascii=False)
                f.write("\n")
        except OSError:
            pass

    def t(self, key: str) -> str:
        """
        Übersetzt einen Key mit mehrstufiger Fallback-Kette:
        Zielsprache -> en -> de -> Key.

        Args:
            key: Translation-Key (z.B. 'btn_analyze_file' oder deutscher Originaltext)

        Returns:
            Übersetzter Text oder Key als Fallback
        """
        entry = self.translations.get(key)
        if isinstance(entry, dict):
            # Fallback-Kette: aktuelle Zielsprache -> 'en' -> 'de'
            for candidate in (self.current_lang, "en", "de"):
                val = entry.get(candidate)
                if val is not None and isinstance(val, str) and val.strip():
                    return val
            return key

        return key

    def set_language(self, lang: str) -> bool:
        """Setzt die aktive Sprache, falls in SUPPORTED_LANGUAGES enthalten."""
        if lang in self.SUPPORTED_LANGUAGES:
            self.current_lang = lang
            return True
        return False

    def get_language(self) -> str:
        """Liefert die aktive Sprache."""
        return self.current_lang

    def get_supported_languages(self) -> List[str]:
        """Liefert die Liste aller unterstützten Sprachcodes."""
        return list(self.SUPPORTED_LANGUAGES)

    def is_supported_language(self, lang: str) -> bool:
        """Prüft, ob ein Sprachcode unterstützt wird."""
        return lang in self.SUPPORTED_LANGUAGES

    def add_translation(self, key: str, translations: Dict[str, str]) -> None:
        """Fügt einen Eintrag mit Übersetzungen hinzu oder aktualisiert ihn."""
        if key not in self.translations:
            self.translations[key] = {}
        if isinstance(self.translations[key], dict):
            self.translations[key].update(translations)
            self._save_translations()

    def scan_and_update(self, project_dir: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """Scannt Projekt-Dateien nach deutschen Strings und aktualisiert translations.json."""
        if project_dir is None:
            p_dir = self.app_dir
        else:
            p_dir = Path(project_dir).resolve()

        found_strings = self._find_german_strings(p_dir)

        added = []
        for string in sorted(found_strings):
            if string not in self.translations:
                self.translations[string] = {lang: string if lang == "de" else "" for lang in self.SUPPORTED_LANGUAGES}
                added.append(string)

        if added:
            self._save_translations()

        missing = [k for k, v in self.translations.items() if isinstance(v, dict) and not v.get("en")]

        return {"added": added, "missing": missing, "total": len(self.translations)}

    def _find_german_strings(self, directory: Path) -> Set[str]:
        german_strings: Set[str] = set()
        skip_dirs = {"build", "dist", "venv", ".venv", "__pycache__", "releases", ".git"}

        for py_file in directory.rglob("*.py"):
            if any(folder in py_file.parts for folder in skip_dirs):
                continue
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue

            for pattern in self.string_patterns:
                for match in pattern.findall(content):
                    if match and self._is_german(match):
                        german_strings.add(match.strip())

        return german_strings

    def _is_german(self, text: str) -> bool:
        if any(ch in text for ch in "äöüÄÖÜß"):
            return True
        text_lower = text.lower()
        return any(hint in text_lower for hint in self.german_hints)

    def get_missing_translations(self, target_lang: str = "en") -> List[str]:
        """Gibt Keys zurück, denen eine Übersetzung in target_lang fehlt."""
        return [
            k for k, v in self.translations.items()
            if isinstance(v, dict) and (target_lang not in v or not str(v[target_lang]).strip())
        ]


if __name__ == "__main__":
    tr = TranslationSystem("de")
    print(f"Sprache: {tr.get_language()}")
    print(f"Unterstützte Sprachen: {tr.get_supported_languages()}")
    result = tr.scan_and_update()
    print(f"Scan: {result['total']} Strings, {len(result['added'])} neu, {len(result['missing'])} ohne EN")
