"""
manage_translations.py - Auto-Scanner für deutsche GUI-Strings
================================================================
Findet deutsche Strings in .py-Dateien und pflegt locales/translations.json.
Validiert Tier-2 6-Sprachen-Parität (DE, EN, ES, ZH, JA, RU).

Verwendung:
    python manage_translations.py [--dir PROJEKTVERZEICHNIS]
    python manage_translations.py --check
    python manage_translations.py --stats
"""

import argparse
import json
import os
import re
import sys

TRANSLATION_FILE = os.path.join("locales", "translations.json")
SUPPORTED_LANGUAGES = ["de", "en", "es", "zh", "ja", "ru"]

STRING_PATTERNS = [
    re.compile(r'text\s*=\s*"([^"]+)"'),
    re.compile(r'setText\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'setWindowTitle\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'QLabel\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'QPushButton\s*\(\s*["\']([^"\']+)["\']\s*\)'),
]

GERMAN_HINTS = [
    "datei", "fehler", "laden", "speichern",
    "ansicht", "optionen", "anzeigen",
    "einstellungen", "abbrechen", "hilfe", "bearbeiten",
    "aktualisieren",
]


def is_german(text):
    if any(ch in text for ch in "\u00e4\u00f6\u00fc\u00c4\u00d6\u00dc\u00df"):
        return True
    text_lower = text.lower()
    return any(w in text_lower for w in GERMAN_HINTS)


def find_german_strings(source_dir):
    german_strings = set()
    skip_dirs = {'build', 'dist', 'venv', '.venv', '__pycache__', 'releases'}

    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                except (OSError, UnicodeError):
                    continue
                for pattern in STRING_PATTERNS:
                    for match in pattern.findall(content):
                        if is_german(match):
                            german_strings.add(match.strip())
    return german_strings


def check_translations(source_dir="."):
    """Prüft ob alle Übersetzungen für alle 6 Sprachen vollständig vorhanden sind."""
    trans_file = os.path.join(source_dir, TRANSLATION_FILE)
    if not os.path.exists(trans_file):
        print(f"[!] Datei nicht gefunden: {trans_file}")
        return False

    try:
        with open(trans_file, "r", encoding="utf-8") as f:
            translations = json.load(f)
    except Exception as e:
        print(f"[!] Fehler beim Laden von {trans_file}: {e}")
        return False

    if not translations or not isinstance(translations, dict):
        print(f"[!] {trans_file} ist leer oder ungültig.")
        return False

    missing_by_lang = {lang: [] for lang in SUPPORTED_LANGUAGES}
    for key, lang_dict in translations.items():
        if not isinstance(lang_dict, dict):
            for lang in SUPPORTED_LANGUAGES:
                missing_by_lang[lang].append(key)
            continue
        for lang in SUPPORTED_LANGUAGES:
            val = lang_dict.get(lang)
            if not val or not str(val).strip():
                missing_by_lang[lang].append(key)

    total_missing = sum(len(m) for m in missing_by_lang.values())
    if total_missing > 0:
        print(f"[!] Fehlende Übersetzungen festgestellt ({total_missing} gesamt über {len(translations)} Schlüssel):")
        for lang, missing_keys in missing_by_lang.items():
            if missing_keys:
                print(f"  [{lang.upper()}]: {len(missing_keys)} fehlend (z.B. {missing_keys[:3]})")
        return False

    print(f"[ok] 100% Parität: Alle {len(translations)} Schlüssel sind in allen 6 Sprachen (DE, EN, ES, ZH, JA, RU) vorhanden.")
    return True


def show_stats(source_dir="."):
    """Zeigt Statistiken über die Übersetzungen an."""
    trans_file = os.path.join(source_dir, TRANSLATION_FILE)
    if not os.path.exists(trans_file):
        print(f"[!] Datei nicht gefunden: {trans_file}")
        return

    try:
        with open(trans_file, "r", encoding="utf-8") as f:
            translations = json.load(f)
    except Exception as e:
        print(f"[!] Fehler beim Laden von {trans_file}: {e}")
        return

    if not isinstance(translations, dict):
        print(f"[!] {trans_file} ist kein gültiges Dictionary.")
        return

    total = len(translations)
    print(f"[i] Gesamtbestand: {total} Schlüssel in {trans_file}")
    for lang in SUPPORTED_LANGUAGES:
        count = sum(1 for v in translations.values() if isinstance(v, dict) and bool(str(v.get(lang, "")).strip()))
        pct = (count / total * 100) if total else 0
        print(f"  {lang.upper()}: {count}/{total} ({pct:.1f}%)")


def manage_translations(source_dir="."):
    trans_file = os.path.join(source_dir, TRANSLATION_FILE)

    if os.path.exists(trans_file):
        try:
            with open(trans_file, "r", encoding="utf-8") as f:
                translations = json.load(f)
        except (OSError, json.JSONDecodeError):
            translations = {}
    else:
        translations = {}

    found = find_german_strings(source_dir)

    added = []
    for s in sorted(found):
        if s not in translations:
            translations[s] = {lang: (s if lang == "de" else "") for lang in SUPPORTED_LANGUAGES}
            added.append(s)

    try:
        os.makedirs(os.path.dirname(trans_file), exist_ok=True)
        with open(trans_file, "w", encoding="utf-8") as f:
            json.dump(translations, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"[FEHLER] translations.json konnte nicht geschrieben werden: {e}", file=sys.stderr)

    if added:
        print(f"[+] {len(added)} neue Einträge hinzugefügt:")
        for s in added[:20]:
            print(f"    - {s}")
        if len(added) > 20:
            print(f"    ... und {len(added) - 20} weitere")
    else:
        print("[i] Keine neuen deutschen Strings gefunden.")

    show_stats(source_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verwalte und prüfe Übersetzungen für MethodenAnalyser.")
    parser.add_argument("pos_dir", nargs="?", default=None, help="Projektverzeichnis (optional)")
    parser.add_argument("--dir", dest="source_dir", default=".", help="Projektverzeichnis")
    parser.add_argument("--check", action="store_true", help="Vollständigkeit der 6 Sprachen prüfen und Exit-Code setzen")
    parser.add_argument("--stats", action="store_true", help="Übersetzungs-Statistiken anzeigen")
    args = parser.parse_args()

    target_dir = args.pos_dir if args.pos_dir else args.source_dir

    if args.check:
        ok = check_translations(target_dir)
        sys.exit(0 if ok else 1)
    elif args.stats:
        show_stats(target_dir)
    else:
        manage_translations(target_dir)
