from __future__ import annotations

import json
import os
import sys
import tempfile
import textwrap
import time
import tkinter as tk
from pathlib import Path
from tkinter import scrolledtext
from typing import Dict, List

from PIL import ImageGrab

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from MethodenAnalyser3 import (
    OUTPUT_FONT,
    OUTPUT_HEIGHT,
    OUTPUT_WIDTH,
    analyze_project,
    analyze_source,
    generate_project_report,
    generate_report,
)


README_SCREENSHOT = PROJECT_ROOT / "README" / "screenshots" / "main.png"
SCREENSHOT_DIR = PROJECT_ROOT / "releases" / "windowsstore" / "screenshots"
MANIFEST_PATH = SCREENSHOT_DIR / "manifest.json"
WINDOW_GEOMETRY = "1440x920"


def _write(path: Path, content: str) -> None:
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")


def _build_file_report() -> str:
    result = analyze_source(
        textwrap.dedent(
            """
            import os
            import json

            def load_settings():
                return {"theme": "light"}

            def helper_debug():
                return os.getcwd()

            print(load_settings())
            """
        ).strip()
        + "\n",
        source_name="settings_panel.py",
    )
    return "Datei-Modus\n\n" + generate_report(result)


def _build_duplicate_report() -> str:
    result = analyze_source(
        textwrap.dedent(
            """
            def normalize_name(value):
                cleaned = value.strip().lower()
                return cleaned.replace("-", "_")

            def normalize_slug(value):
                cleaned = value.strip().lower()
                return cleaned.replace("-", "_")

            print(normalize_name("Demo"))
            """
        ).strip()
        + "\n",
        source_name="duplicate_candidates.py",
    )
    return "Duplikat-Suche\n\n" + generate_report(result)


def _build_project_report() -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        pkg = root / "demo_project"
        pkg.mkdir()
        _write(
            pkg / "main.py",
            """
            import math
            from helper import area

            print(area(2), math.pi)
            """,
        )
        _write(
            pkg / "helper.py",
            """
            import os

            def area(radius):
                return radius * radius * 3.14159

            def unused_helper():
                return os.getcwd()
            """,
        )
        _write(
            pkg / "broken.py",
            """
            def broken(:
                return 1
            """,
        )
        result = analyze_project(str(pkg))
    return "Projekt-Modus\n\n" + generate_project_report(result)


def build_scenarios() -> List[Dict[str, str]]:
    return [
        {
            "filename": "file-analysis.png",
            "title": "Einzeldateien schnell prüfen",
            "subtitle": "AST-basierte Analyse mit ungenutzten Imports und Definitionen",
            "report": _build_file_report(),
        },
        {
            "filename": "project-analysis.png",
            "title": "Projektüberblick mit Sammelreport",
            "subtitle": "Mehrere Python-Dateien inklusive Fehlerdateien gemeinsam auswerten",
            "report": _build_project_report(),
        },
        {
            "filename": "duplicate-detection.png",
            "title": "Ähnliche Code-Blöcke sichtbar machen",
            "subtitle": "Duplikat-Hinweise und Refactoring-Kandidaten im selben Report",
            "report": _build_duplicate_report(),
        },
    ]


def _create_window(report: str, title: str, subtitle: str) -> tk.Tk:
    root = tk.Tk()
    root.title("MethodenAnalyser - Windows Store Screenshots")
    root.geometry(WINDOW_GEOMETRY)
    root.configure(bg="#eef2f7")

    outer = tk.Frame(root, bg="#eef2f7")
    outer.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

    hero = tk.Frame(outer, bg="#102235")
    hero.pack(fill=tk.X, pady=(0, 18))
    tk.Label(
        hero,
        text="MethodenAnalyser",
        font=("Segoe UI", 22, "bold"),
        fg="white",
        bg="#102235",
        anchor="w",
    ).pack(fill=tk.X, padx=22, pady=(20, 4))
    tk.Label(
        hero,
        text=title,
        font=("Segoe UI", 15, "bold"),
        fg="#d8e8ff",
        bg="#102235",
        anchor="w",
    ).pack(fill=tk.X, padx=22)
    tk.Label(
        hero,
        text=subtitle,
        font=("Segoe UI", 11),
        fg="#c0d1e5",
        bg="#102235",
        anchor="w",
    ).pack(fill=tk.X, padx=22, pady=(6, 18))

    button_frame = tk.Frame(outer, bg="#eef2f7")
    button_frame.pack(fill=tk.X, pady=(0, 10))
    buttons = [
        ("📂 Datei analysieren", "#2e7d32"),
        ("ℹ️ Info", "#1565c0"),
        ("🔧 Auto-Fix Imports", "#ef6c00"),
        ("Projekt analysieren", "#7b1fa2"),
    ]
    for text, color in buttons:
        tk.Button(
            button_frame,
            text=text,
            bg=color,
            fg="white",
            relief=tk.FLAT,
            font=("Segoe UI", 10, "bold"),
            padx=18,
            pady=10,
        ).pack(side=tk.LEFT, padx=(0, 8))

    output = scrolledtext.ScrolledText(
        outer,
        width=OUTPUT_WIDTH,
        height=OUTPUT_HEIGHT,
        font=OUTPUT_FONT,
        wrap=tk.WORD,
        bg="#f7f9fc",
        fg="#1f2933",
        bd=0,
        padx=16,
        pady=16,
    )
    output.pack(fill=tk.BOTH, expand=True)
    output.insert("1.0", report)
    output.configure(state=tk.DISABLED)
    return root


def _capture(root: tk.Tk, destination: Path) -> None:
    root.update_idletasks()
    root.update()
    root.lift()
    root.attributes("-topmost", True)
    root.update()
    time.sleep(0.6)
    left = root.winfo_rootx()
    top = root.winfo_rooty()
    right = left + root.winfo_width()
    bottom = top + root.winfo_height()
    image = ImageGrab.grab(bbox=(left, top, right, bottom))
    image.save(destination, "PNG")
    root.destroy()


def generate_store_screenshots() -> Dict[str, object]:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    scenarios = build_scenarios()
    assets = []

    for scenario in scenarios:
        target = SCREENSHOT_DIR / scenario["filename"]
        root = _create_window(
            report=scenario["report"],
            title=scenario["title"],
            subtitle=scenario["subtitle"],
        )
        _capture(root, target)
        assets.append(
            {
                "path": target.name,
                "title": scenario["title"],
                "subtitle": scenario["subtitle"],
            }
        )

    if README_SCREENSHOT.exists():
        (SCREENSHOT_DIR / "main.png").write_bytes(README_SCREENSHOT.read_bytes())
        assets.insert(
            0,
            {
                "path": "main.png",
                "title": "Hauptfenster",
                "subtitle": "Die klassische Desktop-Oberfläche für lokale Python-Dateien",
            },
        )

    manifest = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "count": len(assets),
        "screenshots": assets,
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    manifest = generate_store_screenshots()
    print(f"{manifest['count']} Screenshots aktualisiert: {SCREENSHOT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
