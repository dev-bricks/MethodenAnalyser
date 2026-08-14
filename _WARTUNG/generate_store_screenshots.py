from __future__ import annotations

import json
import sys
import tempfile
import textwrap
import time
import tkinter as tk
from pathlib import Path
from tkinter import scrolledtext
from typing import Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from MethodenAnalyser3 import (  # noqa: E402
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


def _build_file_report(lang: str = "de") -> str:
    header = "File Mode\n\n" if lang == "en" else "Datei-Modus\n\n"
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
    return header + generate_report(result)


def _build_duplicate_report(lang: str = "de") -> str:
    header = "Duplicate Search\n\n" if lang == "en" else "Duplikat-Suche\n\n"
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
    return header + generate_report(result)


def _build_project_report(lang: str = "de") -> str:
    header = "Project Mode\n\n" if lang == "en" else "Projekt-Modus\n\n"
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
    return header + generate_project_report(result)


def get_button_labels(lang: str = "de") -> List[tuple[str, str]]:
    if lang == "en":
        return [
            ("📂 Analyze File", "#2e7d32"),
            ("ℹ️ Info", "#1565c0"),
            ("🔧 Auto-Fix Imports", "#ef6c00"),
            ("Analyze Project", "#7b1fa2"),
        ]
    return [
        ("📂 Datei analysieren", "#2e7d32"),
        ("ℹ️ Info", "#1565c0"),
        ("🔧 Auto-Fix Imports", "#ef6c00"),
        ("Projekt analysieren", "#7b1fa2"),
    ]


def build_scenarios(lang: str = "de") -> List[Dict[str, str]]:
    if lang == "en":
        return [
            {
                "filename": "file-analysis.png",
                "title": "Quickly Analyze Single Files",
                "subtitle": "AST-based analysis detecting unused imports and definitions",
                "report": _build_file_report(lang="en"),
            },
            {
                "filename": "project-analysis.png",
                "title": "Project Overview with Summary Report",
                "subtitle": "Evaluate multiple Python files including error files in a unified report",
                "report": _build_project_report(lang="en"),
            },
            {
                "filename": "duplicate-detection.png",
                "title": "Highlight Similar Code Blocks",
                "subtitle": "Identify duplicate candidates and refactoring targets in one report",
                "report": _build_duplicate_report(lang="en"),
            },
        ]
    return [
        {
            "filename": "file-analysis.png",
            "title": "Einzeldateien schnell prüfen",
            "subtitle": "AST-basierte Analyse mit ungenutzten Imports und Definitionen",
            "report": _build_file_report(lang="de"),
        },
        {
            "filename": "project-analysis.png",
            "title": "Projektüberblick mit Sammelreport",
            "subtitle": "Mehrere Python-Dateien inklusive Fehlerdateien gemeinsam auswerten",
            "report": _build_project_report(lang="de"),
        },
        {
            "filename": "duplicate-detection.png",
            "title": "Ähnliche Code-Blöcke sichtbar machen",
            "subtitle": "Duplikat-Hinweise und Refactoring-Kandidaten im selben Report",
            "report": _build_duplicate_report(lang="de"),
        },
    ]


def _create_window(
    report: str,
    title: str,
    subtitle: str,
    buttons: List[tuple[str, str]] | None = None,
) -> tk.Tk | None:
    try:
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
        btn_items = (
            buttons
            if buttons
            else [
                ("📂 Datei analysieren", "#2e7d32"),
                ("ℹ️ Info", "#1565c0"),
                ("🔧 Auto-Fix Imports", "#ef6c00"),
                ("Projekt analysieren", "#7b1fa2"),
            ]
        )
        for text, color in btn_items:
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
    except Exception:
        return None


def _capture(
    root: tk.Tk | None,
    destination: Path,
    scenario: Dict[str, str] | None = None,
    buttons_list: List[tuple[str, str]] | None = None,
) -> None:
    from PIL import Image, ImageDraw, ImageFont, ImageGrab

    captured = False
    if root is not None:
        try:
            root.update_idletasks()
            root.update()
            root.lift()
            root.attributes("-topmost", True)
            root.update()
            time.sleep(0.4)
            left = root.winfo_rootx()
            top = root.winfo_rooty()
            right = left + root.winfo_width()
            bottom = top + root.winfo_height()
            if right > left and bottom > top:
                image = ImageGrab.grab(bbox=(left, top, right, bottom))
                image.save(destination, "PNG")
                captured = True
        except Exception:
            captured = False
        finally:
            try:
                root.destroy()
            except Exception:
                pass

    if not captured:
        width, height = 1440, 920
        img = Image.new("RGB", (width, height), color="#eef2f7")
        draw = ImageDraw.Draw(img)

        # Draw hero header (#102235)
        draw.rectangle([24, 24, width - 24, 150], fill="#102235")

        try:
            font_title = ImageFont.truetype("segoeui.ttf", 22)
            font_sub1 = ImageFont.truetype("segoeuib.ttf", 15)
            font_sub2 = ImageFont.truetype("segoeui.ttf", 11)
            font_btn = ImageFont.truetype("segoeuib.ttf", 10)
            font_body = ImageFont.truetype("consola.ttf", 10)
        except Exception:
            font_title = font_sub1 = font_sub2 = font_btn = font_body = (
                ImageFont.load_default()
            )

        draw.text((46, 40), "MethodenAnalyser", fill="white", font=font_title)

        sub1_text = scenario["title"] if scenario else "MethodenAnalyser"
        sub2_text = scenario["subtitle"] if scenario else ""
        draw.text((46, 75), sub1_text, fill="#d8e8ff", font=font_sub1)
        draw.text((46, 105), sub2_text, fill="#c0d1e5", font=font_sub2)

        # Draw buttons
        btn_x = 24
        btn_y = 162
        if buttons_list:
            for text, color in buttons_list:
                btn_w = len(text) * 9 + 30
                draw.rectangle(
                    [btn_x, btn_y, btn_x + btn_w, btn_y + 36], fill=color
                )
                draw.text(
                    (btn_x + 12, btn_y + 10), text, fill="white", font=font_btn
                )
                btn_x += btn_w + 10

        # Draw report box (#f7f9fc)
        draw.rectangle(
            [24, 210, width - 24, height - 24], fill="#f7f9fc", outline="#d1d5db"
        )
        report_text = scenario["report"] if scenario else ""
        draw.text(
            (40, 226), report_text[:3000], fill="#1f2933", font=font_body
        )

        destination.parent.mkdir(parents=True, exist_ok=True)
        img.save(destination, "PNG")


def generate_store_screenshots(lang: str = "de") -> Dict[str, object]:
    target_dir = (
        SCREENSHOT_DIR / lang if lang in ("de", "en") else SCREENSHOT_DIR
    )
    target_dir.mkdir(parents=True, exist_ok=True)
    if lang == "de":
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    scenarios = build_scenarios(lang=lang)
    buttons = get_button_labels(lang=lang)
    assets = []

    for scenario in scenarios:
        target = target_dir / scenario["filename"]
        root = _create_window(
            report=scenario["report"],
            title=scenario["title"],
            subtitle=scenario["subtitle"],
            buttons=buttons,
        )
        _capture(root, target, scenario=scenario, buttons_list=buttons)
        if lang == "de":
            (SCREENSHOT_DIR / scenario["filename"]).write_bytes(
                target.read_bytes()
            )

        assets.append(
            {
                "path": scenario["filename"],
                "title": scenario["title"],
                "subtitle": scenario["subtitle"],
            }
        )

    main_title = "Main Window" if lang == "en" else "Hauptfenster"
    main_sub = (
        "The classic desktop interface for local Python files"
        if lang == "en"
        else "Die klassische Desktop-Oberfläche für lokale Python-Dateien"
    )

    if README_SCREENSHOT.exists():
        (target_dir / "main.png").write_bytes(README_SCREENSHOT.read_bytes())
        if lang == "de":
            (SCREENSHOT_DIR / "main.png").write_bytes(
                README_SCREENSHOT.read_bytes()
            )
        assets.insert(
            0,
            {
                "path": "main.png",
                "title": main_title,
                "subtitle": main_sub,
            },
        )

    manifest = {
        "language": lang,
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "count": len(assets),
        "screenshots": assets,
    }

    manifest_path = target_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if lang == "de":
        MANIFEST_PATH.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    return manifest


def generate_all_store_screenshots() -> Dict[str, Dict[str, object]]:
    return {
        "de": generate_store_screenshots(lang="de"),
        "en": generate_store_screenshots(lang="en"),
    }


def main() -> int:
    results = generate_all_store_screenshots()
    print(
        f"Screenshots updated: DE={results['de']['count']} ({SCREENSHOT_DIR / 'de'}), "
        f"EN={results['en']['count']} ({SCREENSHOT_DIR / 'en'})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
