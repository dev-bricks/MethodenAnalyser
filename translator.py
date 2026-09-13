"""
TranslationSystem - Multi-Language Support für Anwendungen
============================================================
Version: 1.1.0 (P-006 Standard)
Quelle: ARC_EntwicklungsschleifeAdvanced/TranslationSystem.py v2.4 + MethodenAnalyser

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
from typing import Dict, List, Optional, Set, Union


class TranslationSystem:
    """Multi-Language Support System v1.1 (P-006 Standard)"""

    SUPPORTED_LANGUAGES: List[str] = ["de", "en", "es", "zh", "ja", "ru"]
    DEFAULT_LANGUAGE: str = "de"
    FALLBACK_LANGUAGE: str = "en"
    LANGUAGES_DISPLAY: Dict[str, str] = {
        "de": "Deutsch",
        "en": "English",
        "es": "Español",
        "zh": "中文",
        "ja": "日本語",
        "ru": "Русский",
    }

    def __init__(self, default_lang: str = "de", app_dir: Optional[Union[Path, str]] = None):
        """
        Initialisiert Translation-System.

        Args:
            default_lang: Standard-Sprache ('de', 'en', 'es', 'zh', 'ja', 'ru')
            app_dir: Verzeichnis der Anwendung (default: Verzeichnis dieser Datei)
        """
        if default_lang in self.SUPPORTED_LANGUAGES:
            self.current_lang = default_lang
        else:
            self.current_lang = self.DEFAULT_LANGUAGE

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

        self.translations: Dict[str, Union[Dict[str, str], str]] = {}
        self._load_translations()

    def _load_translations(self) -> None:
        """Lädt Übersetzungen aus translations.json mit robustem Error-Handling."""
        if self.translations_file.exists():
            try:
                with open(self.translations_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.translations = data if isinstance(data, dict) else {}
            except Exception:
                self.translations = {}
        else:
            self.translations = {}

    def _save_translations(self) -> bool:
        """Speichert Übersetzungen in translations.json."""
        try:
            self.translations_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.translations_file, "w", encoding="utf-8") as f:
                json.dump(self.translations, f, indent=2, ensure_ascii=False)
                f.write("\n")
            return True
        except OSError:
            return False

    def t(self, key: str, **kwargs) -> str:
        """
        Übersetzt einen Key in die aktuelle Sprache gem. P-006 mehrstufiger Fallback-Kette:
        1. Zielsprache (self.current_lang)
        2. Fallback-Sprache Englisch ('en')
        3. Standard-Sprache Deutsch ('de')
        4. Key selbst

        Args:
            key: Translation-Key
            **kwargs: Optionale Formatierungs-Parameter ({name})

        Returns:
            Übersetzter formatierter Text oder Key als Fallback
        """
        entry = self.translations.get(key)
        if isinstance(entry, dict):
            text = entry.get(self.current_lang)
            if not text and self.current_lang != self.FALLBACK_LANGUAGE:
                text = entry.get(self.FALLBACK_LANGUAGE)
            if not text and self.current_lang != self.DEFAULT_LANGUAGE:
                text = entry.get(self.DEFAULT_LANGUAGE)
            if not text:
                text = key
            if kwargs:
                try:
                    return text.format(**kwargs)
                except (KeyError, IndexError, ValueError):
                    return text
            return text
        elif entry is not None:
            text = str(entry) if isinstance(entry, str) else key
            if kwargs:
                try:
                    return text.format(**kwargs)
                except (KeyError, IndexError, ValueError):
                    pass
            return text

        if self._is_german(key):
            self.translations[key] = {"de": key, "en": ""}
            self._save_translations()

        if kwargs:
            try:
                return key.format(**kwargs)
            except (KeyError, IndexError, ValueError):
                pass

        return key

    def set_language(self, lang: str) -> bool:
        """
        Setzt die aktuelle Sprache, wenn sie unterstützt wird.

        Returns:
            True bei Erfolg, False wenn Sprache nicht in SUPPORTED_LANGUAGES.
        """
        if lang in self.SUPPORTED_LANGUAGES:
            self.current_lang = lang
            return True
        return False

    def get_language(self) -> str:
        """Gibt die aktuell eingestellte Sprache zurück."""
        return self.current_lang

    def get_supported_languages(self) -> List[str]:
        """Gibt die Liste aller unterstützten Sprachen zurück."""
        return list(self.SUPPORTED_LANGUAGES)

    def get_language_display_name(self, lang: str) -> str:
        """Gibt den Anzeigenamen einer Sprache zurück (z.B. 'Español' für 'es')."""
        return self.LANGUAGES_DISPLAY.get(lang, lang)

    def add_translation(
        self,
        key: str,
        de_or_dict: Union[str, Dict[str, str]],
        en: Optional[str] = None,
        **extra_langs,
    ) -> None:
        """
        Fügt eine Übersetzung hinzu und speichert die Datei.
        Unterstützt sowohl add_translation(k, de, en) als auch add_translation(k, {'de': ..., 'en': ...}).
        """
        if isinstance(de_or_dict, dict):
            self.translations[key] = de_or_dict
        else:
            trans_dict = {"de": de_or_dict, "en": en or ""}
            trans_dict.update(extra_langs)
            self.translations[key] = trans_dict
        self._save_translations()

    def scan_and_update(self, project_dir: Optional[Union[Path, str]] = None) -> Dict[str, Any]:
        """Scannt Projekt-Dateien nach deutschen Strings und aktualisiert translations.json."""
        if project_dir is None:
            target_dir = self.app_dir
        else:
            target_dir = Path(project_dir).resolve()

        found_strings = self._find_german_strings(target_dir)

        added = []
        for string in sorted(found_strings):
            if string not in self.translations:
                self.translations[string] = {"de": string, "en": ""}
                added.append(string)

        if added:
            self._save_translations()

        missing = [
            k for k, v in self.translations.items()
            if isinstance(v, dict) and not v.get("en")
        ]

        return {"added": added, "missing": missing, "total": len(self.translations)}

    def _find_german_strings(self, directory: Path) -> Set[str]:
        german_strings = set()
        skip_dirs = {"build", "dist", "venv", ".venv", "__pycache__", "releases"}

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

    def get_missing_translations(self, lang: str = "en") -> List[str]:
        """Gibt Keys zurück, bei denen die Übersetzung für 'lang' fehlt."""
        missing = []
        for k, v in self.translations.items():
            if isinstance(v, dict):
                if not v.get(lang):
                    missing.append(k)
            else:
                missing.append(k)
        return missing


if __name__ == "__main__":
    tr = TranslationSystem("de")
    print(f"Sprache: {tr.get_language()} (Verfügbar: {', '.join(tr.get_supported_languages())})")
    result = tr.scan_and_update()
    print(f"Scan: {result['total']} Strings, {len(result['added'])} neu, {len(result['missing'])} ohne EN")
