import ast
import json
import os
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


if __name__ == "__main__":
    unittest.main()
