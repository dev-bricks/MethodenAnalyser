import base64
import io
import threading
import unittest
import zipfile
from http.server import ThreadingHTTPServer
from urllib.request import urlopen

from webapp.server import MethodenAnalyserPwaHandler, analyze_payload, build_runtime_info


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

    def test_runtime_info_for_local_only_server(self) -> None:
        info = build_runtime_info("127.0.0.1", 8765, address_supplier=lambda: ["192.168.0.5"])

        self.assertTrue(info["local_only"])
        self.assertFalse(info["candidate_urls"])
        self.assertEqual(info["mobile_command"], "python webapp/server.py --host 0.0.0.0 --port 8765")

    def test_runtime_info_for_wildcard_server_includes_lan_urls(self) -> None:
        info = build_runtime_info(
            "0.0.0.0",
            8765,
            address_supplier=lambda: ["10.0.0.8", "192.168.0.5"],
        )

        self.assertFalse(info["local_only"])
        self.assertTrue(info["mobile_ready"])
        self.assertEqual(
            info["candidate_urls"],
            ["http://10.0.0.8:8765/", "http://192.168.0.5:8765/"],
        )


class MethodenAnalyserStaticHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), MethodenAnalyserPwaHandler)
        cls.port = cls.httpd.server_address[1]
        cls.httpd.runtime_info = build_runtime_info("127.0.0.1", cls.port)
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

    def test_index_includes_json_import_controls(self) -> None:
        with urlopen(self.build_url("/")) as response:
            body = response.read().decode("utf-8")

        self.assertIn('id="importJson"', body)
        self.assertIn('id="reportFile"', body)
        self.assertIn('id="refreshPwaStatus"', body)
        self.assertIn('id="copyPwaStatus"', body)
        self.assertIn('id="pwaServerValue"', body)

    def test_runtime_endpoint_returns_mobile_metadata(self) -> None:
        with urlopen(self.build_url("/api/runtime")) as response:
            payload = response.read().decode("utf-8")

        self.assertIn('"ok": true', payload)
        self.assertIn('"local_only": true', payload)
        self.assertIn('"local_url": "http://127.0.0.1:', payload)
        self.assertIn('"mobile_command": "python webapp/server.py --host 0.0.0.0 --port', payload)


if __name__ == "__main__":
    unittest.main()
