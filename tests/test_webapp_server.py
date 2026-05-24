import unittest

from webapp.server import analyze_payload


class MethodenAnalyserWebappServerTests(unittest.TestCase):
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
            analyze_payload({"code": "print('ok')\n", "source_kind": "zip"})


if __name__ == "__main__":
    unittest.main()
