import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _WARTUNG import generate_store_screenshots as shots


class StoreScreenshotTests(unittest.TestCase):
    def test_build_scenarios_returns_expected_entries_de_and_en(self) -> None:
        scenarios_de = shots.build_scenarios(lang="de")
        self.assertEqual([entry["filename"] for entry in scenarios_de], [
            "file-analysis.png",
            "project-analysis.png",
            "duplicate-detection.png",
        ])
        self.assertTrue(all(entry["title"] for entry in scenarios_de))
        self.assertTrue(all("report" in entry and entry["report"] for entry in scenarios_de))
        self.assertIn("Einzeldateien", scenarios_de[0]["title"])

        scenarios_en = shots.build_scenarios(lang="en")
        self.assertEqual([entry["filename"] for entry in scenarios_en], [
            "file-analysis.png",
            "project-analysis.png",
            "duplicate-detection.png",
        ])
        self.assertTrue(all(entry["title"] for entry in scenarios_en))
        self.assertIn("Analyze", scenarios_en[0]["title"])

    def test_generate_store_screenshots_writes_manifest_de_and_en(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            screenshot_dir = tmp_path / "screenshots"
            manifest_path = screenshot_dir / "manifest.json"
            readme_shot = tmp_path / "main.png"
            readme_shot.write_bytes(b"png")
            touched = []

            def fake_capture(_root, destination: Path, **_kwargs) -> None:
                destination.write_bytes(b"png")
                touched.append(destination.name)

            with mock.patch.object(shots, "SCREENSHOT_DIR", screenshot_dir), \
                    mock.patch.object(shots, "MANIFEST_PATH", manifest_path), \
                    mock.patch.object(shots, "README_SCREENSHOT", readme_shot), \
                    mock.patch.object(shots, "_create_window", side_effect=lambda **_: object()), \
                    mock.patch.object(shots, "_capture", side_effect=fake_capture):
                results = shots.generate_all_store_screenshots()
                manifest_de_payload = json.loads((screenshot_dir / "de" / "manifest.json").read_text(encoding="utf-8"))
                manifest_en_payload = json.loads((screenshot_dir / "en" / "manifest.json").read_text(encoding="utf-8"))

            self.assertEqual(results["de"]["count"], 4)
            self.assertEqual(results["en"]["count"], 4)
            self.assertEqual(manifest_de_payload["language"], "de")
            self.assertEqual(manifest_en_payload["language"], "en")
            self.assertEqual(manifest_en_payload["screenshots"][1]["title"], "Quickly Analyze Single Files")


if __name__ == "__main__":
    unittest.main()
