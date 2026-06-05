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
        """TOOL_VERSION muss mit der Versionsangabe im Info-Dialog übereinstimmen."""
        source = SCRIPT_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)

        tool_version = None
        info_dialog_version = None

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "TOOL_VERSION":
                        if isinstance(node.value, ast.Constant):
                            tool_version = node.value.value

            # f-string: f"Python Code Analyzer v{TOOL_VERSION}\n\n"
            if isinstance(node, ast.JoinedStr):
                for part in node.values:
                    if isinstance(part, ast.FormattedValue):
                        if isinstance(part.value, ast.Name) and part.value.id == "TOOL_VERSION":
                            info_dialog_version = "TOOL_VERSION_ref"

        self.assertIsNotNone(tool_version, "TOOL_VERSION nicht gefunden")
        self.assertIsNotNone(
            info_dialog_version,
            "Info-Dialog referenziert TOOL_VERSION nicht als f-string — Versions-Mismatch möglich",
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


if __name__ == "__main__":
    unittest.main()
