import pathlib
import tempfile
import unittest

from MethodenAnalyser3 import (
    ProjectAnalysisResult,
    analyze_project,
    build_json_report,
    collect_python_files,
    generate_project_report,
)


class CollectFilesAndProjectAnalysisTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base = pathlib.Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_collect_python_files_supports_wildcards_and_globs(self) -> None:
        """collect_python_files must exclude files matching glob patterns like test_* or *.generated.py."""
        (self.base / "main.py").write_text("x = 1\n", encoding="utf-8")
        (self.base / "test_main.py").write_text("y = 2\n", encoding="utf-8")
        (self.base / "data_generated.py").write_text("z = 3\n", encoding="utf-8")
        (self.base / "helper.tmp.py").write_text("w = 4\n", encoding="utf-8")

        # Exclude using wildcard patterns
        files = collect_python_files(
            str(self.base),
            exclude_patterns=["test_*", "*_generated.py", "*.tmp.py"],
        )
        names = [pathlib.Path(f).name for f in files]
        self.assertIn("main.py", names)
        self.assertNotIn("test_main.py", names, "Wildcard 'test_*' should have excluded test_main.py")
        self.assertNotIn("data_generated.py", names, "Wildcard '*_generated.py' should have excluded data_generated.py")
        self.assertNotIn("helper.tmp.py", names, "Wildcard '*.tmp.py' should have excluded helper.tmp.py")

    def test_collect_python_files_supports_nested_path_patterns(self) -> None:
        """collect_python_files must support exclude patterns with path separators."""
        fixtures_dir = self.base / "tests" / "fixtures"
        fixtures_dir.mkdir(parents=True)
        (fixtures_dir / "sample.py").write_text("a = 1\n", encoding="utf-8")

        other_dir = self.base / "tests" / "other"
        other_dir.mkdir(parents=True)
        (other_dir / "keep.py").write_text("b = 2\n", encoding="utf-8")

        # Exclude specific sub-path
        files = collect_python_files(str(self.base), exclude_patterns=["tests/fixtures"])
        names = [pathlib.Path(f).name for f in files]
        self.assertNotIn("sample.py", names, "Pattern 'tests/fixtures' should have excluded tests/fixtures/sample.py")
        self.assertIn("keep.py", names)

    def test_collect_python_files_raises_on_nonexistent_and_file(self) -> None:
        """collect_python_files must validate folder_path."""
        nonexistent = str(self.base / "nonexistent_dir")
        with self.assertRaises(FileNotFoundError):
            collect_python_files(nonexistent)

        a_file = self.base / "some_file.py"
        a_file.write_text("print('hi')\n", encoding="utf-8")
        with self.assertRaises(NotADirectoryError):
            collect_python_files(str(a_file))

    def test_analyze_project_accepts_and_forwards_exclude_patterns(self) -> None:
        """analyze_project must accept exclude_patterns and forward them to collect_python_files."""
        (self.base / "keep.py").write_text("def keep(): pass\n", encoding="utf-8")
        (self.base / "skip_me.py").write_text("def skip(): pass\n", encoding="utf-8")

        result = analyze_project(str(self.base), exclude_patterns=["skip_me*"])
        analyzed_names = [pathlib.Path(f).name for f in result.file_results]
        self.assertIn("keep.py", analyzed_names)
        self.assertNotIn("skip_me.py", analyzed_names, "analyze_project should have forwarded exclude_patterns")

    def test_generate_project_report_uses_relative_paths_for_errors(self) -> None:
        """generate_project_report must print relative paths for files_with_errors."""
        bad_file = self.base / "sub" / "broken.py"
        bad_file.parent.mkdir(parents=True)
        bad_file.write_text("def broken(:\n", encoding="utf-8")

        result = analyze_project(str(self.base))
        self.assertEqual(len(result.files_with_errors), 1)

        report = generate_project_report(result)
        # Full absolute path should not appear in error listing when relative path is available
        self.assertIn("sub/broken.py", report.replace("\\", "/"))
        self.assertNotIn(str(bad_file), report, "generate_project_report should display relative paths for files_with_errors")

    def test_build_json_report_safe_error_paths(self) -> None:
        """build_json_report must safely normalize error paths without raising ValueError."""
        dummy_result = ProjectAnalysisResult(
            folder_path=str(self.base),
            files_analyzed=0,
            files_with_errors=[(str(self.base / "broken.py"), "SyntaxError")],
            total_lines=0,
            total_defs=0,
            total_imports=0,
            all_unused_imports={},
            all_unused_defs={},
            all_missing_defs={},
            all_missing_imports={},
            all_duplicate_imports={},
            file_results={},
        )
        report = build_json_report("project", dummy_result)
        self.assertEqual(len(report["errors"]), 1)
        self.assertEqual(report["errors"][0]["path"], "broken.py")

    def test_collect_python_files_prunes_excluded_directories(self) -> None:
        """collect_python_files prunes excluded directory trees like .venv, .git, and node_modules."""
        (self.base / "app").mkdir(parents=True)
        (self.base / "app" / "main.py").write_text("x = 1\n", encoding="utf-8")

        venv_dir = self.base / ".venv" / "Lib" / "site-packages"
        venv_dir.mkdir(parents=True)
        (venv_dir / "dep.py").write_text("y = 2\n", encoding="utf-8")

        git_dir = self.base / ".git" / "hooks"
        git_dir.mkdir(parents=True)
        (git_dir / "hook.py").write_text("z = 3\n", encoding="utf-8")

        node_dir = self.base / "node_modules" / "sub"
        node_dir.mkdir(parents=True)
        (node_dir / "tool.py").write_text("w = 4\n", encoding="utf-8")

        files = collect_python_files(str(self.base))
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].endswith("main.py"))

    def test_analyze_project_computes_total_lines_from_results(self) -> None:
        """analyze_project calculates total_lines accurately via AnalysisResult.total_lines."""
        (self.base / "file1.py").write_text("a = 1\nb = 2\nc = 3\n", encoding="utf-8")
        (self.base / "file2.py").write_text("def f():\n    return 42\n", encoding="utf-8")

        result = analyze_project(str(self.base))
        self.assertEqual(result.files_analyzed, 2)
        self.assertEqual(result.total_lines, 5)
