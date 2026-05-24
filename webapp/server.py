from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STATIC_ROOT = Path(__file__).resolve().parent / "static"
ASSETS_ROOT = PROJECT_ROOT / "store_assets"
MAX_REQUEST_SIZE = 512 * 1024

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from MethodenAnalyser3 import (  # noqa: E402
    _file_has_findings,
    analyze_source,
    build_json_report,
    generate_report,
)


mimetypes.add_type("application/manifest+json", ".webmanifest")
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/css", ".css")


def _clean_filename(filename: Any, source_kind: str) -> str:
    if not isinstance(filename, str) or not filename.strip():
        return "<snippet>" if source_kind == "snippet" else "upload.py"
    clean = filename.strip().replace("\\", "/").split("/")[-1]
    return clean or ("<snippet>" if source_kind == "snippet" else "upload.py")


def analyze_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Analyze browser-submitted Python code and return API-ready JSON."""
    code = payload.get("code")
    if not isinstance(code, str) or not code.strip():
        raise ValueError("Python-Code fehlt.")

    source_kind = payload.get("source_kind", "snippet")
    if source_kind not in {"snippet", "file"}:
        raise ValueError("source_kind muss 'snippet' oder 'file' sein.")

    filename = _clean_filename(payload.get("filename"), source_kind)
    result = analyze_source(code, source_name=filename)
    report = build_json_report(source_kind, result, source_name=filename)
    return {
        "ok": True,
        "has_findings": _file_has_findings(result),
        "text_report": generate_report(result),
        "report": report,
    }


def _resolve_under(root: Path, relative_path: str) -> Path | None:
    root = root.resolve()
    target = (root / relative_path).resolve()
    if target == root or root not in target.parents:
        return None
    if not target.is_file():
        return None
    return target


class MethodenAnalyserPwaHandler(BaseHTTPRequestHandler):
    server_version = "MethodenAnalyserPWA/0.1"

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/health":
            self._send_json({"ok": True, "service": "methodenanalyser-webapp"})
            return
        if path.startswith("/assets/"):
            asset_name = unquote(path.removeprefix("/assets/"))
            target = _resolve_under(ASSETS_ROOT, asset_name)
            self._send_file_or_404(target)
            return

        relative = "index.html" if path in {"", "/"} else unquote(path.lstrip("/"))
        target = _resolve_under(STATIC_ROOT, relative)
        self._send_file_or_404(target)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/api/analyze":
            self._send_json({"ok": False, "error": "Unbekannter Endpunkt."}, status=404)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json({"ok": False, "error": "Ungültiger Content-Length."}, status=400)
            return

        if length <= 0:
            self._send_json({"ok": False, "error": "Leerer Request."}, status=400)
            return
        if length > MAX_REQUEST_SIZE:
            self._send_json(
                {"ok": False, "error": "Request ist größer als 512 KB."},
                status=413,
            )
            return

        try:
            raw_body = self.rfile.read(length).decode("utf-8")
            payload = json.loads(raw_body)
            if not isinstance(payload, dict):
                raise ValueError("JSON-Body muss ein Objekt sein.")
            response = analyze_payload(payload)
        except json.JSONDecodeError as exc:
            self._send_json({"ok": False, "error": f"Ungültiges JSON: {exc}"}, status=400)
            return
        except SyntaxError as exc:
            self._send_json({"ok": False, "error": f"Python-Syntaxfehler: {exc}"}, status=422)
            return
        except ValueError as exc:
            self._send_json({"ok": False, "error": str(exc)}, status=400)
            return
        except Exception as exc:
            self._send_json({"ok": False, "error": f"Analyse fehlgeschlagen: {exc}"}, status=500)
            return

        self._send_json(response)

    def _send_file_or_404(self, target: Path | None) -> None:
        if target is None:
            self._send_json({"ok": False, "error": "Datei nicht gefunden."}, status=404)
            return

        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        try:
            body = target.read_bytes()
        except OSError as exc:
            self._send_json({"ok": False, "error": f"Datei kann nicht gelesen werden: {exc}"}, status=500)
            return

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        if target.name == "index.html":
            self.send_header("Content-Security-Policy", "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self'")
        if target.name == "service-worker.js":
            self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Startet den lokalen MethodenAnalyser Web/PWA-Companion.")
    parser.add_argument("--host", default="127.0.0.1", help="Host/IP für den lokalen Server")
    parser.add_argument("--port", type=int, default=8765, help="Port für den lokalen Server")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    server = ThreadingHTTPServer((args.host, args.port), MethodenAnalyserPwaHandler)
    url = f"http://{args.host}:{args.port}/"
    print(f"MethodenAnalyser Web/PWA läuft lokal unter {url}")
    print("Beenden mit Strg+C.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer beendet.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
