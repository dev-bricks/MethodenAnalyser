import base64
import io
import threading
import unittest
import zipfile
from http.server import ThreadingHTTPServer
from urllib.request import urlopen

from webapp.server import MethodenAnalyserPwaHandler, analyze_payload


class MethodenAnalyserWebappServerTests(unittest.TestCase):
    def make_zip_payload(self, files: dict[str, str], filename: str = "sample.zip") -> dict[str, str]:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path, content in files.items():
                archive.writestr(path, content)
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        return {
            "source_kind": "zip",
            "filename": filename,
            "zip_base64": encoded,
        }

    def test_snippet_payload_returns_json_report(self) -> None:
        payload = analyze_payload(
            {
                "code": "import os\nprint('ok')\n",
                "source_kind": "snippet",
                "filename": "<snippet>",
            }
        )

        self.assertTrue(payload["ok"])
        self.assertTrue(payload["has_findings"])
        self.assertEqual(payload["report"]["schema_version"], "methodenanalyser-report-v1")
        self.assertEqual(payload["report"]["source_kind"], "snippet")
        self.assertEqual(payload["report"]["unused_imports"]["<snippet>"], ["os"])

    def test_file_payload_keeps_basename_only(self) -> None:
        payload = analyze_payload(
            {
                "code": "import math\nprint(math.pi)\n",
                "source_kind": "file",
                "filename": r"C:\private\demo.py",
            }
        )

        self.assertEqual(payload["report"]["files"][0]["path"], "demo.py")
        self.assertFalse(payload["has_findings"])

    def test_rejects_missing_code(self) -> None:
        with self.assertRaises(ValueError):
            analyze_payload({"code": "", "source_kind": "snippet"})

    def test_rejects_unknown_source_kind(self) -> None:
        with self.assertRaises(ValueError):
            analyze_payload({"code": "print('ok')\n", "source_kind": "folder"})

    def test_zip_payload_returns_project_report(self) -> None:
        payload = analyze_payload(
            self.make_zip_payload(
                {
                    "pkg/main.py": "import math\nprint(math.pi)\n",
                    "pkg/helper.py": "import os\nprint('helper')\n",
                    "README.txt": "ignored",
                },
                filename="demo_bundle.zip",
            )
        )

        self.assertTrue(payload["ok"])
        self.assertTrue(payload["has_findings"])
        self.assertEqual(payload["report"]["source_kind"], "zip")
        self.assertEqual(payload["report"]["source"]["name"], "demo_bundle.zip")
        self.assertEqual(payload["report"]["source"]["archive_entries"], 2)
        self.assertEqual(payload["report"]["summary"]["files_analyzed"], 2)
        self.assertIn("PROJEKT CODE ANALYSE", payload["text_report"])
        self.assertEqual(sorted(entry["path"] for entry in payload["report"]["files"]), ["pkg/helper.py", "pkg/main.py"])

    def test_zip_payload_rejects_path_traversal(self) -> None:
        with self.assertRaises(ValueError):
            analyze_payload(
                self.make_zip_payload(
                    {
                        "../escape.py": "print('nope')\n",
                    }
                )
            )


class MethodenAnalyserStaticHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), MethodenAnalyserPwaHandler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=2)

    def build_url(self, path: str) -> str:
        return f"http://127.0.0.1:{self.port}{path}"

    def test_manifest_is_served_with_expected_fields(self) -> None:
        with urlopen(self.build_url("/manifest.webmanifest")) as response:
            body = response.read().decode("utf-8")
            content_type = response.headers.get_content_type()

        self.assertEqual(content_type, "application/manifest+json")
        self.assertIn('"display": "standalone"', body)
        self.assertIn('"orientation": "portrait-primary"', body)

    def test_service_worker_disables_cache_header(self) -> None:
        with urlopen(self.build_url("/service-worker.js")) as response:
            body = response.read().decode("utf-8")
            cache_control = response.headers.get("Cache-Control")

        self.assertEqual(cache_control, "no-cache")
        self.assertIn('"/offline.html"', body)

    def test_offline_page_is_reachable(self) -> None:
        with urlopen(self.build_url("/offline.html")) as response:
            body = response.read().decode("utf-8")

        self.assertIn("MethodenAnalyser ist offline bereit", body)


if __name__ == "__main__":
    unittest.main()
