<p align="center">
  <img src="https://img.shields.io/badge/Version-3.0-blue?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.10+-yellow?style=for-the-badge" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/GUI-Tkinter-orange?style=for-the-badge" alt="GUI">
  <img src="https://img.shields.io/badge/Deps-None-brightgreen?style=for-the-badge" alt="No Dependencies">
</p>

<h1 align="center">MethodenAnalyser</h1>

<h4 align="center">Statischer Python-Code-Analyser mit GUI — findet ungenutzte Imports, tote Definitionen und aehnliche Code-Bloecke</h4>

---

## Features

| Feature | Beschreibung |
|---------|-------------|
| **AST-Analyse** | Praezise Analyse via Python Abstract Syntax Tree |
| **Import-Tracking** | Erkennt genutzte und ungenutzte Imports |
| **Methoden-Katalog** | Listet alle Funktionen, Methoden und Klassen |
| **Duplikat-Erkennung** | Findet aehnliche Code-Bloecke (konfigurierbarer Schwellwert, Standard: 80%) |
| **Framework-Erkennung** | Erkennt ob Definitionen von Tkinter, requests, asyncio u.a. implizit genutzt werden |
| **Callback-Erkennung** | Identifiziert Callback-Funktionen korrekt als genutzt |
| **Multi-File** | Ganze Python-Projekte rekursiv analysieren |
| **GUI** | Einfache Tkinter-Oberflaeche, kein Terminal noetig |

### Was unterscheidet MethodenAnalyser von pylint / flake8 / vulture?

| Feature | MethodenAnalyser | pylint | flake8 | vulture | radon |
|---------|:---:|:---:|:---:|:---:|:---:|
| Ungenutzte Imports | ✅ | ✅ | ⚠️ | ✅ | ❌ |
| Ungenutzte Definitionen | ✅ | ⚠️ | ❌ | ✅ | ❌ |
| **Code-Aehnlichkeit** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Framework-Erkennung** | ✅ | ⚠️ | ❌ | ❌ | ❌ |
| **GUI** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Callback-Erkennung** | ✅ | ❌ | ❌ | ⚠️ | ❌ |
| Keine Installation | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## Installation

Keine externen Abhaengigkeiten. Nur Python 3.10+ benoetigt.

```bash
git clone https://github.com/lukisch/MethodenAnalyser.git
cd MethodenAnalyser
python MethodenAnalyser3.py
```

Oder unter Windows per Doppelklick auf `START.bat`.

---

## Verwendung

### Einzelne Datei analysieren

1. Tool starten (`python MethodenAnalyser3.py` oder `START.bat`)
2. **"Datei analysieren"** klicken und `.py`-Datei auswaehlen
3. Ergebnisse werden im Ausgabefenster angezeigt

### Ganzes Projekt analysieren

1. **"Projekt analysieren"** klicken und Projektordner auswaehlen
2. Alle `.py`-Dateien werden rekursiv durchsucht
3. Aggregierter Projekt-Report mit Score wird ausgegeben

---

## Beispiel-Output

```
=== ANALYSE: my_script.py ===

IMPORTS (3 gesamt):
  ✅ os           — genutzt
  ✅ json         — genutzt
  ⚠️  pathlib      — moeglicherweise ungenutzt

DEFINITIONEN (5 gesamt):
  ✅ main()
  ✅ load_config()
  ⚠️  old_helper() — nicht referenziert

AEHNLICHE CODE-BLOECKE (Schwellwert: 80%):
  Zeilen 42-55 ↔ Zeilen 88-101  (Aehnlichkeit: 91%)
```

---

## Konfiguration

Im Quellcode anpassbar:

```python
SIMILARITY_THRESHOLD = 0.8   # Schwellwert fuer Duplikat-Erkennung (0.0 - 1.0)
WINDOW_GEOMETRY = "1200x700" # Fenstergrösse
```

---

## Lizenz

Dieses Projekt steht unter der [MIT License](LICENSE).

---

## English

A static Python code analyzer with AST analysis, duplicate detection, and GUI.

### Features

- AST-based analysis
- Duplicate code detection
- Method complexity metrics
- Interactive GUI

### Installation

```bash
git clone https://github.com/lukisch/REL-PUB_MethodenAnalyser.git
cd REL-PUB_MethodenAnalyser
pip install -r requirements.txt
python "MethodenAnalyser3.py"
```

### License

See [LICENSE](LICENSE) for details.
