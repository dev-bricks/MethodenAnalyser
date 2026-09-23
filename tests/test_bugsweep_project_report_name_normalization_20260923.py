import pathlib
import tempfile
import unittest

from MethodenAnalyser3 import (
    ProjectAnalysisResult,
    build_json_report,
    generate_project_report,
)


class ProjectReportNameNormalizationTests(unittest.TestCase):
    """Bug-Sweep Tests 2026-09-23: Normalisierung von Projektnamen bei Slash-Endungen und relativen Pfaden."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base = pathlib.Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_generate_project_report_handles_trailing_slash(self) -> None:
        """generate_project_report darf bei trailing slash keinen leeren Projektnamen anzeigen."""
        proj_dir = self.base / "my_project"
        proj_dir.mkdir()
        dummy_result = ProjectAnalysisResult(
            folder_path=str(proj_dir) + "/",
            files_analyzed=1,
            files_with_errors=[],
            total_lines=10,
            total_defs=1,
            total_imports=1,
            all_unused_imports={},
            all_unused_defs={},
            all_missing_defs={},
            all_missing_imports={},
            all_duplicate_imports={},
            file_results={},
        )
        report = generate_project_report(dummy_result)
        self.assertIn("my_project", report, "Projektname darf bei trailing slash nicht leer sein")
        self.assertNotIn("Projekt: \n", report, "Projektzeile darf nicht leer enden")

    def test_generate_project_report_handles_dot_and_slash(self) -> None:
        """generate_project_report soll bei '.' oder './' den tatsächlichen Ordnernamen ermitteln."""
        dummy_result = ProjectAnalysisResult(
            folder_path=".",
            files_analyzed=1,
            files_with_errors=[],
            total_lines=10,
            total_defs=1,
            total_imports=1,
            all_unused_imports={},
            all_unused_defs={},
            all_missing_defs={},
            all_missing_imports={},
            all_duplicate_imports={},
            file_results={},
        )
        report = generate_project_report(dummy_result)
        current_dir_name = pathlib.Path(".").resolve().name
        self.assertIn(current_dir_name, report)
        self.assertNotIn("Projekt: .\n", report, "Projektname sollte aufgelöst werden statt '.' anzuzeigen")

    def test_generate_project_report_accepts_custom_project_name(self) -> None:
        """generate_project_report soll optionalen project_name Parameter akzeptieren (z.B. für Webapp ZIP-Uploads)."""
        dummy_result = ProjectAnalysisResult(
            folder_path=str(self.base),
            files_analyzed=1,
            files_with_errors=[],
            total_lines=10,
            total_defs=1,
            total_imports=1,
            all_unused_imports={},
            all_unused_defs={},
            all_missing_defs={},
            all_missing_imports={},
            all_duplicate_imports={},
            file_results={},
        )
        report = generate_project_report(dummy_result, project_name="archive_upload.zip")
        self.assertIn("archive_upload.zip", report)

    def test_build_json_report_handles_trailing_slash_in_project_and_source_name(self) -> None:
        """build_json_report darf bei trailing slash im Projektnamen oder source_name keinen leeren String liefern."""
        dummy_result = ProjectAnalysisResult(
            folder_path=str(self.base / "cool_app") + "/",
            files_analyzed=1,
            files_with_errors=[],
            total_lines=10,
            total_defs=1,
            total_imports=1,
            all_unused_imports={},
            all_unused_defs={},
            all_missing_defs={},
            all_missing_imports={},
            all_duplicate_imports={},
            file_results={},
        )
        report = build_json_report("project", dummy_result, source_name="cool_app/")
        self.assertEqual(report["source"]["name"], "cool_app")


if __name__ == "__main__":
    unittest.main()
