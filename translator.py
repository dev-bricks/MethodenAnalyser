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
import locale
import os
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


LOCALE_PREFIX_MAP: dict[str, str] = {
    "de": "de",
    "ger": "de",
    "deutsch": "de",
    "en": "en",
    "eng": "en",
    "english": "en",
    "es": "es",
    "spa": "es",
    "spanish": "es",
    "espanol": "es",
    "zh": "zh",
    "chi": "zh",
    "chinese": "zh",
    "ja": "ja",
    "jpn": "ja",
    "japanese": "ja",
    "ru": "ru",
    "rus": "ru",
    "russian": "ru",
}


def normalize_language_code(code: Optional[str]) -> Optional[str]:
    """Normalisiert einen Sprachcode oder Bezeichner auf die unterstützten Sprachen."""
    if not code or not isinstance(code, str):
        return None
    cleaned = code.strip().lower().replace("-", "_")
    if not cleaned:
        return None
    short_code = cleaned.split("_")[0]
    if short_code in TranslationSystem.SUPPORTED_LANGUAGES:
        return short_code
    for prefix, mapped in LOCALE_PREFIX_MAP.items():
        if cleaned.startswith(prefix):
            return mapped
    return None


def detect_system_language(default: str = "de") -> str:
    """Ermittelt die bevorzugte Systemsprache aus Umgebungsvariablen oder System-Locale."""
    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        val = os.environ.get(var)
        detected = normalize_language_code(val)
        if detected:
            return detected

    try:
        loc = locale.getlocale()[0]
        detected = normalize_language_code(loc)
        if detected:
            return detected
    except Exception:
        pass

    try:
        loc = locale.getdefaultlocale()[0]
        detected = normalize_language_code(loc)
        if detected:
            return detected
    except Exception:
        pass

    return default if default in TranslationSystem.SUPPORTED_LANGUAGES else TranslationSystem.DEFAULT_LANGUAGE


def detect_language_from_header(accept_language: Optional[str]) -> Optional[str]:
    """Parst einen HTTP Accept-Language Header und liefert die bevorzugte unterstützte Sprache."""
    if not accept_language or not isinstance(accept_language, str):
        return None

    candidates: list[tuple[float, str]] = []
    for part in accept_language.split(","):
        segment = part.strip()
        if not segment:
            continue
        subparts = segment.split(";")
        code = subparts[0].strip()
        q_val = 1.0
        for param in subparts[1:]:
            param = param.strip()
            if param.startswith("q="):
                try:
                    q_val = float(param[2:].strip())
                except ValueError:
                    q_val = 0.0
        normalized = normalize_language_code(code)
        if normalized:
            candidates.append((q_val, normalized))

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


if __name__ == "__main__":
    tr = TranslationSystem("de")
    print(f"Sprache: {tr.get_language()}")
    print(f"Unterstützte Sprachen: {tr.get_supported_languages()}")
    print(f"System-Sprache: {detect_system_language()}")
    result = tr.scan_and_update()
    print(f"Scan: {result['total']} Strings, {len(result['added'])} neu, {len(result['missing'])} ohne EN")
