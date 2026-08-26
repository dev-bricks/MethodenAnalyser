"""Regression contracts for the documented Windows build path."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class BuildContractTests(unittest.TestCase):
    def test_batch_and_build_documents_describe_the_same_pyinstaller_path(self) -> None:
        script = (ROOT / "build_exe.bat").read_text(encoding="utf-8")
        build_doc = (ROOT / "BUILD.md").read_text(encoding="utf-8")
        crosscheck = (ROOT / "_sources" / "CROSSCHECK.md").read_text(encoding="utf-8")

        for marker in (
            "python -m PyInstaller",
            "--windowed --onefile",
            "%EXCLUDES%",
            '--specpath "%BUILD_ROOT%"',
            '"%PROJECT_ROOT%\\MethodenAnalyser3.py"',
        ):
            self.assertIn(marker, script)

        for document in (build_doc, crosscheck):
            self.assertIn("PyInstaller", document)
            self.assertIn("MethodenAnalyser3.py", document)
            self.assertIn("--windowed --onefile", document)
            self.assertIn("MethodenAnalyser.spec", document)
            self.assertIn("nicht eingelesen", document)
            self.assertIn("ohne dynamische Excludes", document)
            self.assertIn(r"dist\MethodenAnalyser.exe", document)


if __name__ == "__main__":
    unittest.main()
