import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _WARTUNG import generate_store_screenshots as shots


class StoreScreenshotTests(unittest.TestCase):
    def test_build_scenarios_returns_expected_entries(self) -> None:
        scenarios = shots.build_scenarios()

        self.assertEqual([entry["filename"] for entry in scenarios], [
            "file-analysis.png",
            "project-analysis.png",
            "duplicate-detection.png",
        ])
        self.assertTrue(all(entry["title"] for entry in scenarios))
        self.assertTrue(all("report" in entry and entry["report"] for entry in scenarios))

    def test_generate_store_screenshots_writes_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            screenshot_dir = tmp_path / "screenshots"
            manifest_path = screenshot_dir / "manifest.json"
            readme_shot = tmp_path / "main.png"
            readme_shot.write_bytes(b"png")
            touched = []

            def fake_capture(_root, destination: Path) -> None:
                destination.write_bytes(b"png")
                touched.append(destination.name)

            with mock.patch.object(shots, "SCREENSHOT_DIR", screenshot_dir), \
                    mock.patch.object(shots, "MANIFEST_PATH", manifest_path), \
                    mock.patch.object(shots, "README_SCREENSHOT", readme_shot), \
                    mock.patch.object(shots, "_create_window", side_effect=lambda **_: object()), \
                    mock.patch.object(shots, "_capture", side_effect=fake_capture):
                manifest = shots.generate_store_screenshots()
                payload = json.loads(manifest_path.read_text(encoding="utf-8"))

            self.assertEqual(touched, [
                "file-analysis.png",
                "project-analysis.png",
                "duplicate-detection.png",
            ])
            self.assertEqual(manifest["count"], 4)
        self.assertEqual(payload["screenshots"][0]["path"], "main.png")
        self.assertEqual(payload["screenshots"][1]["path"], "file-analysis.png")


if __name__ == "__main__":
    unittest.main()
