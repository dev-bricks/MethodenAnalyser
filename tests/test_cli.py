import ast
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "MethodenAnalyser3.py"


class MethodenAnalyserCliTests(unittest.TestCase):
    def run_cli(
        self,
        *args: str,
        input_text: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *args],
            input=input_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
            check=False,
            timeout=30,
        )

    def test_file_mode_returns_zero_for_clean_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sample = Path(tmpdir) / "clean_sample.py"
            sample.write_text(
                textwrap.dedent(
                    """
                    import math

                    def area(radius):
                        return math.pi * radius * radius

                    print(area(2))
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            result = self.run_cli("--file", str(sample))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PYTHON CODE ANALYSE - ERGEBNISSE", result.stdout)
        self.assertIn("Ungenutzte Imports (0):", result.stdout)

    def test_cli_language_switches_help_and_summary_without_persisting_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sample = Path(tmpdir) / "clean_sample.py"
            sample.write_text("print('ok')\n", encoding="utf-8")
            result = self.run_cli("--lang", "en", "--file", str(sample))
        help_result = self.run_cli("--lang", "en", "--help")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PYTHON CODE ANALYSIS - RESULTS", result.stdout)
        self.assertIn("Unused Imports (0):", result.stdout)
        self.assertIn("--file FILE.py", help_result.stdout)
        self.assertIn("show this help message and exit", help_result.stdout)
        self.assertIn("analyzes one Python file", help_result.stdout)
        self.assertIn("reads Python code from stdin", help_result.stdout)
        self.assertIn("also writes a JSON report", help_result.stdout)
        self.assertNotIn("analysiert eine einzelne Python-Datei", help_result.stdout)

    def test_file_mode_writes_json_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            sample = tmp_path / "clean_sample.py"
            report_path = tmp_path / "methodenanalyser-report-v1.json"
            sample.write_text(
                textwrap.dedent(
                    """
                    import math

                    def area(radius):
                        return math.pi * radius * radius

                    print(area(2))
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            result = self.run_cli(
                "--file",
                str(sample),
                "--json-output",
                str(report_path),
            )
            payload = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(payload["schema_version"], "methodenanalyser-report-v1")
        self.assertEqual(payload["source_kind"], "file")
        self.assertEqual(payload["files"][0]["path"], "clean_sample.py")
        self.assertEqual(payload["summary"]["unused_imports"], 0)

    def test_file_mode_returns_findings_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sample = Path(tmpdir) / "findings_sample.py"
            sample.write_text(
                textwrap.dedent(
                    """
                    import os

                    def helper():
                        return 1

                    print("ok")
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            result = self.run_cli("--file", str(sample))

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("Ungenutzte Definitionen", result.stdout)
        self.assertIn("helper", result.stdout)

    def test_project_mode_returns_partial_error_for_broken_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir) / "demo_project"
            project.mkdir()
            (project / "good.py").write_text("print('ok')\n", encoding="utf-8")
            (project / "broken.py").write_text("def broken(:\n", encoding="utf-8")

            result = self.run_cli("--project", str(project))

        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertIn("PROJEKT CODE ANALYSE", result.stdout)
        self.assertIn("DATEIEN MIT FEHLERN", result.stdout)
        self.assertIn("broken.py", result.stdout)

    def test_project_mode_writes_json_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir) / "demo_project"
            project.mkdir()
            report_path = Path(tmpdir) / "project-report.json"
            (project / "good.py").write_text("print('ok')\n", encoding="utf-8")

            result = self.run_cli(
                "--project",
                str(project),
                "--json-output",
                str(report_path),
            )
            payload = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(payload["source_kind"], "project")
        self.assertEqual(payload["summary"]["files_analyzed"], 1)
        self.assertEqual(payload["files"][0]["path"], "good.py")

    def test_stdin_snippet_writes_json_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "snippet-report.json"

            result = self.run_cli(
                "--stdin",
                "--json-output",
                str(report_path),
                input_text="import os\nprint('ok')\n",
            )
            payload = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(payload["source_kind"], "snippet")
        self.assertEqual(payload["files"][0]["path"], "<snippet>")
        self.assertEqual(payload["unused_imports"]["<snippet>"], ["os"])

    def test_missing_file_returns_analysis_error(self) -> None:
        result = self.run_cli("--file", str(PROJECT_ROOT / "does_not_exist.py"))

        self.assertEqual(result.returncode, 1)
        self.assertIn("[FEHLER]", result.stderr)

    def test_info_dialog_version_matches_tool_version(self) -> None:
        """Der Info-Dialog muss seine Versionsangabe aus TOOL_VERSION ableiten."""
        source = SCRIPT_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)

        tool_version = None
        version_from_tool_version = False

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "TOOL_VERSION":
                        if isinstance(node.value, ast.Constant):
                            tool_version = node.value.value

            # Variante A (f-string): f"Python Code Analyzer v{TOOL_VERSION}\n\n"
            if isinstance(node, ast.JoinedStr):
                for part in node.values:
                    if isinstance(part, ast.FormattedValue):
                        if isinstance(part.value, ast.Name) and part.value.id == "TOOL_VERSION":
                            version_from_tool_version = True

            # Variante B (i18n): _t("info_body").replace("{version}", TOOL_VERSION)
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "replace"
                and any(
                    isinstance(arg, ast.Name) and arg.id == "TOOL_VERSION"
                    for arg in node.args
                )
            ):
                version_from_tool_version = True

        self.assertIsNotNone(tool_version, "TOOL_VERSION nicht gefunden")
        self.assertTrue(
            version_from_tool_version,
            "Info-Dialog leitet die Version nicht aus TOOL_VERSION ab — Versions-Mismatch möglich",
        )

        # i18n-Absicherung: die info_body-Uebersetzungen muessen den {version}-Platzhalter
        # tragen, sonst liefe die TOOL_VERSION-Ersetzung ins Leere.
        translations = json.loads(
            (PROJECT_ROOT / "locales" / "translations.json").read_text(encoding="utf-8")
        )
        info_body = translations.get("info_body", {})
        for lang in ("de", "en"):
            self.assertIn(
                "{version}",
                info_body.get(lang, ""),
                f"info_body[{lang}] muss den Platzhalter {{version}} enthalten",
            )


class RegressionTests(unittest.TestCase):
    """Regression-Tests für Bugfixes."""

    def run_cli(self, *args: str, input_text: str | None = None, extra_env: dict | None = None) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        if extra_env:
            env.update(extra_env)
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *args],
            input=input_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
            check=False,
            timeout=30,
        )

    def test_report_text_contains_no_emojis(self) -> None:
        """Regression (Bug A): generate_report() darf keine Emojis enthalten —
        UnicodeEncodeError auf Windows cp1252 wenn stdout nicht UTF-8."""
        sys.path.insert(0, str(PROJECT_ROOT))
        from MethodenAnalyser3 import analyze_source, generate_report
        code = (
            "import os\n"
            "import re\n"
            "from threading import Thread, Lock\n"
            "def helper(): pass\n"
            "x = Thread(target=helper)\n"
            "x.start()\n"
        )
        result = analyze_source(code)
        report = generate_report(result)
        # Alle Zeichen müssen in cp1252 (Windows-Standardencoding) encodierbar sein.
        try:
            report.encode("cp1252")
        except UnicodeEncodeError as e:
            self.fail(
                f"generate_report() enthält nicht-cp1252-encodierbare Zeichen: {e}\n"
                "Bitte Emojis durch ASCII-Marker ersetzen."
            )

    def test_collect_python_files_excludes_exact_dir_names_only(self) -> None:
        """Regression (Bug C): collect_python_files() darf 'build' nicht als
        Substring matchen — Pfade wie 'C:/Users/builder/...' dürfen NICHT
        ausgeschlossen werden."""
        sys.path.insert(0, str(PROJECT_ROOT))
        from MethodenAnalyser3 import collect_python_files
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            base = pathlib.Path(tmpdir)
            # Ordner mit Namen der "build" als Substring enthalten, aber KEIN build/-Ordner
            builder_dir = base / "builder"
            builder_dir.mkdir()
            (builder_dir / "main.py").write_text("x = 1\n", encoding="utf-8")

            # Echter build/-Ordner — soll exkludiert werden
            build_dir = base / "build"
            build_dir.mkdir()
            (build_dir / "output.py").write_text("y = 2\n", encoding="utf-8")

            files = collect_python_files(str(base))

        names = [pathlib.Path(f).name for f in files]
        self.assertIn("main.py", names, "Datei in 'builder/'-Ordner muss eingeschlossen sein")
        self.assertNotIn("output.py", names, "Datei in 'build/'-Ordner muss ausgeschlossen sein")

    def test_project_cli_handles_permission_error_gracefully(self) -> None:
        """Regression (Bug B): _run_cli_project muss Exception aus analyze_project
        abfangen und Exit-Code 1 liefern statt unbehandelt zu crashen."""
        import tempfile
        import unittest.mock
        import io

        sys.path.insert(0, str(PROJECT_ROOT))
        from MethodenAnalyser3 import _run_cli_project, EXIT_ANALYSIS_ERROR

        with tempfile.TemporaryDirectory() as tmpdir:
            captured = io.StringIO()
            with unittest.mock.patch(
                "MethodenAnalyser3.analyze_project",
                side_effect=RuntimeError("simulated permission error"),
            ), unittest.mock.patch("sys.stderr", captured):
                exit_code = _run_cli_project(tmpdir)

        self.assertEqual(exit_code, EXIT_ANALYSIS_ERROR)
        self.assertIn("[FEHLER]", captured.getvalue())

    def test_auto_fix_removes_multiline_imports_completely(self) -> None:
        """Regression (Bug D): _collect_unused_import_lines() muss mehrzeilige
        Klammer-Imports vollständig markieren (alle Zeilen lineno..end_lineno),
        nicht nur die erste Zeile."""
        import ast as _ast

        sys.path.insert(0, str(PROJECT_ROOT))
        from MethodenAnalyser3 import _collect_unused_import_lines

        code = (
            "from threading import (\n"
            "    Thread,\n"
            "    Lock\n"
            ")\n"
            "x = 1\n"
        )
        tree = _ast.parse(code)
        lines_to_remove = _collect_unused_import_lines(tree, {"Thread", "Lock"})

        # Alle 4 Import-Zeilen (1-4) müssen markiert sein
        self.assertEqual(lines_to_remove, {1, 2, 3, 4},
                         "Mehrzeiliger Import muss alle Zeilen (lineno..end_lineno) markieren")

        # Ergebnis-Datei muss syntaktisch valide Python sein
        all_lines = code.splitlines(keepends=True)
        remaining = [line for i, line in enumerate(all_lines, 1) if i not in lines_to_remove]
        remaining_code = "".join(remaining)
        try:
            _ast.parse(remaining_code)
        except SyntaxError as e:
            self.fail(f"Nach Entfernen des mehrzeiligen Imports ist das Ergebnis kein valides Python: {e}")


    def test_scan_dynamic_usage_excludes_pattern_markers_from_methods(self) -> None:
        """Regression (B-003): scan_dynamic_usage() darf 'getattr(' und 'setattr('
        NICHT als extrahierte Methodennamen zurueckgeben — nur echte Bezeichner."""
        sys.path.insert(0, str(PROJECT_ROOT))
        from MethodenAnalyser3 import scan_dynamic_usage

        code = (
            "handler = getattr(self, 'on_click')\n"
            "setattr(self, 'x', 1)\n"
            "result = eval('1+1')\n"
        )
        _, dynamic_methods = scan_dynamic_usage(code)

        for bad_token in ("getattr(", "setattr(", "eval("):
            self.assertNotIn(
                bad_token,
                dynamic_methods,
                f"'{bad_token}' ist kein Methodenname und darf nicht in dynamic_methods erscheinen",
            )

    def test_collect_unused_import_lines_handles_dotted_imports(self) -> None:
        """Regression (B-002): _collect_unused_import_lines() muss 'import os.path'
        als entfernbar markieren wenn 'os' in unused_set ist.
        alias.name='os.path' != 'os', deshalb split('.')[0] noetig."""
        import ast as _ast

        sys.path.insert(0, str(PROJECT_ROOT))
        from MethodenAnalyser3 import _collect_unused_import_lines

        code = "import os.path\nx = 1\n"
        tree = _ast.parse(code)
        lines_to_remove = _collect_unused_import_lines(tree, {"os"})

        self.assertEqual(
            lines_to_remove,
            {1},
            "import os.path muss als entfernbar markiert werden wenn 'os' ungenutzt ist",
        )

    def test_collect_unused_import_lines_keeps_future_imports(self) -> None:
        """Regression (Bug D): from __future__ import annotations darf nicht entfernt
        werden, auch wenn 'annotations' nicht explizit als Name genutzt wird."""
        import ast as _ast
        sys.path.insert(0, str(PROJECT_ROOT))
        from MethodenAnalyser3 import _collect_unused_import_lines

        code = "from __future__ import annotations\nimport os\nx = 1\n"
        tree = _ast.parse(code)
        lines_to_remove = _collect_unused_import_lines(tree, {"annotations", "os"})

        self.assertNotIn(1, lines_to_remove, "__future__-Import darf nicht entfernt werden")
        self.assertIn(2, lines_to_remove, "normaler unbenutzter Import muss markiert werden")


class TestEncodingHandling(unittest.TestCase):
    """Tests für Encoding-Fallback bei nicht-UTF-8-Dateien (Latin-1)."""

    def setUp(self):
        sys.path.insert(0, str(PROJECT_ROOT))
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_analyze_project_latin1_file_not_in_errors(self) -> None:
        """Regression (Bug B): analyze_project() darf latin-1-Dateien nicht in
        files_with_errors listen, wenn die Analyse per Encoding-Fallback erfolgreich war."""
        from MethodenAnalyser3 import analyze_project

        latin1_code = b"# encoding: latin-1\nimport os\nx = 'caf\xe9'\n"
        file_path = os.path.join(self.tmpdir, "latin1_file.py")
        with open(file_path, "wb") as f:
            f.write(latin1_code)

        result = analyze_project(self.tmpdir)

        error_paths = [e[0] for e in result.files_with_errors]
        self.assertNotIn(
            file_path,
            error_paths,
            "latin-1-Datei darf nicht in files_with_errors stehen wenn Analyse erfolgreich war",
        )
        self.assertEqual(result.files_analyzed, 1)

    def _call_auto_fix(self, filepath, result):
        """Setzt Globals, ruft auto_fix_unused_imports mit gemockter GUI auf."""
        import unittest.mock
        import MethodenAnalyser3 as m3
        orig_path = m3._last_analysis_path
        orig_result = m3._last_analysis_result
        try:
            m3._last_analysis_path = filepath
            m3._last_analysis_result = result
            with unittest.mock.patch("MethodenAnalyser3.messagebox") as mb:
                mb.askyesno.return_value = True
                m3.auto_fix_unused_imports(unittest.mock.MagicMock())
        finally:
            m3._last_analysis_path = orig_path
            m3._last_analysis_result = orig_result

    def test_auto_fix_works_on_latin1_file(self) -> None:
        """Regression (Bug A): auto_fix_unused_imports() darf bei latin-1-Dateien
        nicht mit UnicodeDecodeError abstuerzen und muss den Import korrekt entfernen."""
        import MethodenAnalyser3 as m3

        latin1_code = b"import os\nimport sys\nx = 'caf\xe9'\nprint(sys.argv)\n"
        filepath = os.path.join(self.tmpdir, "latin1_autofix.py")
        with open(filepath, "wb") as f:
            f.write(latin1_code)

        result = m3.analyze_file(filepath)
        self.assertIn("os", result.unused_imports)

        self._call_auto_fix(filepath, result)

        with open(filepath, "r", encoding="latin-1") as f:
            content = f.read()
        self.assertNotIn("import os\n", content)
        self.assertIn("import sys\n", content)

    def test_auto_fix_form_feed_line_alignment(self) -> None:
        """Regression (Fix A): Form-Feed \\x0c darf AST-Zeilennummern nicht verschieben
        — splitlines() wuerde bei \\x0c extra Zeilen erzeugen, readlines() nicht."""
        import MethodenAnalyser3 as m3

        # \x0c vor import os: splitlines() wuerde Zeile 1=leer, 2=import os sehen,
        # AST sieht aber lineno=1 fuer import os — readlines() bleibt konsistent.
        code = b"\x0cimport os\nimport sys\nprint(os.getcwd())\n"
        filepath = os.path.join(self.tmpdir, "formfeed_autofix.py")
        with open(filepath, "wb") as f:
            f.write(code)

        result = m3.analyze_file(filepath)
        self.assertIn("sys", result.unused_imports)
        self.assertNotIn("os", result.unused_imports)

        self._call_auto_fix(filepath, result)

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("import sys", content)
        self.assertIn("import os", content)

    def test_auto_fix_preserves_latin1_encoding_for_non_ascii_content(self) -> None:
        """Regression (Bug C): auto_fix darf bei latin-1-Dateien das Encoding nicht auf
        UTF-8 aendern — wuerde Dateien mit '# coding: latin-1' und nicht-ASCII korrumpieren."""
        import MethodenAnalyser3 as m3

        # Datei mit latin-1 Nicht-ASCII-Zeichen (café = caf + \xe9)
        latin1_code = b"import os\nimport sys\nx = 'caf\xe9'\nprint(sys.argv)\n"
        filepath = os.path.join(self.tmpdir, "latin1_nonascii.py")
        with open(filepath, "wb") as f:
            f.write(latin1_code)

        result = m3.analyze_file(filepath)
        self.assertIn("os", result.unused_imports)

        self._call_auto_fix(filepath, result)

        # Datei muss weiterhin als latin-1 lesbar sein (kein UnicodeDecodeError)
        with open(filepath, "rb") as f:
            raw_bytes = f.read()
        # Das nicht-ASCII-Byte \xe9 (é in latin-1) muss erhalten bleiben
        self.assertIn(b"\xe9", raw_bytes, "latin-1 Byte \\xe9 darf nach auto_fix nicht fehlen")
        # Darf NICHT als UTF-8-Sequenz \xc3\xa9 codiert worden sein
        self.assertNotIn(b"\xc3\xa9", raw_bytes, "Encoding darf nicht von latin-1 auf UTF-8 geaendert worden sein")


class TestExceptHandlerAndDunders(unittest.TestCase):
    """Tests für Bug E (ExceptHandler-Binding) und Bug F (Module-Dunders)."""

    def setUp(self):
        sys.path.insert(0, str(PROJECT_ROOT))

    def test_except_binding_not_in_missing_imports(self) -> None:
        """Regression (Bug E): 'except Exception as e:' darf 'e' nicht als
        missing_import ausweisen — ExceptHandler.name ist ein str, kein ast.Name-Knoten."""
        from MethodenAnalyser3 import analyze_source

        code = textwrap.dedent("""
            import sys

            def run():
                try:
                    pass
                except Exception as e:
                    print(e)
        """).strip() + "\n"

        result = analyze_source(code)
        self.assertNotIn(
            "e",
            result.missing_imports,
            "Exception-Binding 'e' darf nicht als missing_import erscheinen",
        )

    def test_module_dunders_not_in_missing_imports(self) -> None:
        """Regression (Bug F): __file__, __name__, __doc__ sind implizit verfuegbar
        und duerfen nicht als missing_imports erscheinen."""
        from MethodenAnalyser3 import analyze_source

        code = textwrap.dedent("""
            def info():
                print(__file__, __name__, __doc__)
        """).strip() + "\n"

        result = analyze_source(code)
        for dunder in ("__file__", "__name__", "__doc__"):
            self.assertNotIn(
                dunder,
                result.missing_imports,
                f"{dunder} ist implizit verfuegbar und darf nicht in missing_imports stehen",
            )


class TranslatorIsGermanTests(unittest.TestCase):
    """Tests für TranslationSystem._is_german()."""

    def setUp(self):
        sys.path.insert(0, str(PROJECT_ROOT))
        from translator import TranslationSystem
        self.tr = TranslationSystem.__new__(TranslationSystem)
        self.tr.german_hints = [
            "datei", "bearbeiten", "ansicht", "hilfe", "speichern",
            "einstellungen", "abbrechen", "ja", "nein",
        ]

    def test_english_words_not_classified_as_german(self) -> None:
        """Regression (B-001): _is_german() darf englische Woerter nicht als deutsch
        klassifizieren — war fehlerhaft mit 'aeoeueAeOeUess' als ASCII-Zeichenmenge."""
        for word in ("error", "success", "open", "close", "Python", "import", "run", "test"):
            with self.subTest(word=word):
                self.assertFalse(
                    self.tr._is_german(word),
                    f"'{word}' ist kein deutsches Wort und darf nicht als deutsch erkannt werden",
                )

    def test_german_umlaut_words_classified_as_german(self) -> None:
        """Woerter mit echten Umlauten muessen als deutsch erkannt werden."""
        for word in ("Öffnen", "schließen", "Übersicht", "Änderung", "Größe"):
            with self.subTest(word=word):
                self.assertTrue(
                    self.tr._is_german(word),
                    f"'{word}' enthaelt Umlaute und muss als deutsch erkannt werden",
                )


class GuiShortcutTests(unittest.TestCase):
    def test_keyboard_shortcut_hint_mentions_primary_actions(self) -> None:
        sys.path.insert(0, str(PROJECT_ROOT))
        from MethodenAnalyser3 import _get_keyboard_shortcut_hint

        hint = _get_keyboard_shortcut_hint()

        self.assertIn("Alt+D", hint)
        self.assertIn("Alt+P", hint)
        self.assertIn("Alt+F", hint)
        self.assertIn("F1", hint)

    def test_register_gui_shortcuts_binds_and_invokes_callbacks(self) -> None:
        sys.path.insert(0, str(PROJECT_ROOT))
        from MethodenAnalyser3 import _register_gui_shortcuts

        class FakeRoot:
            def __init__(self) -> None:
                self.bindings = {}

            def bind_all(self, sequence, handler) -> None:
                self.bindings[sequence] = handler

        calls = []

        def mark(name: str):
            def _callback() -> None:
                calls.append(name)

            return _callback

        root = FakeRoot()
        _register_gui_shortcuts(
            root,
            analyze_file_cb=mark("file"),
            info_cb=mark("info"),
            auto_fix_cb=mark("fix"),
            analyze_project_cb=mark("project"),
        )

        for sequence in ("<Alt-d>", "<Alt-D>", "<Alt-p>", "<Alt-P>", "<Alt-f>", "<Alt-F>", "<F1>"):
            self.assertIn(sequence, root.bindings)

        self.assertEqual(root.bindings["<Alt-d>"](None), "break")
        self.assertEqual(root.bindings["<Alt-P>"](None), "break")
        self.assertEqual(root.bindings["<Alt-f>"](None), "break")
        self.assertEqual(root.bindings["<F1>"](None), "break")
        self.assertEqual(calls, ["file", "project", "fix", "info"])


if __name__ == "__main__":
    unittest.main()
