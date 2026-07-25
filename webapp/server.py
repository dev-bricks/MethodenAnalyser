from __future__ import annotations

import argparse
import base64
import binascii
import io
import ipaddress
import json
import socket
import sys
import tempfile
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STATIC_ROOT = Path(__file__).resolve().parent / "static"
ASSETS_ROOT = PROJECT_ROOT / "store_assets"
MAX_REQUEST_SIZE = 2 * 1024 * 1024
MAX_ZIP_FILE_COUNT = 64
MAX_ZIP_MEMBER_SIZE = 512 * 1024
MAX_ZIP_TOTAL_BYTES = 2 * 1024 * 1024

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from MethodenAnalyser3 import (  # noqa: E402
    _file_has_findings,
    _project_has_findings,
    analyze_project,
    analyze_source,
    build_json_report,
    generate_project_report,
    generate_report,
)


LOCAL_ONLY_HOSTS = {"127.0.0.1", "::1", "localhost"}
WILDCARD_HOSTS = {"0.0.0.0", "::"}
CONTENT_TYPES_BY_SUFFIX = {
    ".css": "text/css; charset=utf-8",
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".png": "image/png",
    ".webmanifest": "application/manifest+json; charset=utf-8",
}


def _clean_filename(filename: Any, source_kind: str) -> str:
    if not isinstance(filename, str) or not filename.strip():
        if source_kind == "snippet":
            return "<snippet>"
        if source_kind == "zip":
            return "upload.zip"
        return "upload.py"

    clean = filename.strip().replace("\\", "/").split("/")[-1]
    if clean:
        return clean
    if source_kind == "snippet":
        return "<snippet>"
    if source_kind == "zip":
        return "upload.zip"
    return "upload.py"


def _decode_zip_bytes(encoded_zip: Any) -> bytes:
    if not isinstance(encoded_zip, str) or not encoded_zip.strip():
        raise ValueError("ZIP-Inhalt fehlt.")

    payload = encoded_zip.strip()
    if payload.startswith("data:") and "," in payload:
        payload = payload.split(",", 1)[1]

    try:
        return base64.b64decode(payload, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("ZIP-Inhalt ist kein gültiges Base64-Archiv.") from exc


def _safe_zip_members(archive: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    python_members: list[zipfile.ZipInfo] = []
    total_size = 0

    for info in archive.infolist():
        if info.is_dir():
            continue

        relative_path = PurePosixPath(info.filename.replace("\\", "/"))
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise ValueError(f"Unsicherer ZIP-Pfad erkannt: {info.filename}")
        if relative_path.suffix.lower() != ".py":
            continue

        if len(python_members) >= MAX_ZIP_FILE_COUNT:
            raise ValueError(f"ZIP enthält mehr als {MAX_ZIP_FILE_COUNT} Python-Dateien.")
        if info.file_size > MAX_ZIP_MEMBER_SIZE:
            raise ValueError(
                f"ZIP-Datei {info.filename} ist größer als {MAX_ZIP_MEMBER_SIZE // 1024} KB."
            )

        total_size += info.file_size
        if total_size > MAX_ZIP_TOTAL_BYTES:
            raise ValueError(f"ZIP enthält mehr als {MAX_ZIP_TOTAL_BYTES // 1024} KB Python-Code.")

        python_members.append(info)

    if not python_members:
        raise ValueError("ZIP-Archiv enthält keine Python-Dateien.")

    return python_members


def _extract_python_zip(zip_bytes: bytes, target_root: Path) -> int:
    target_root = target_root.resolve()
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        members = _safe_zip_members(archive)
        for info in members:
            relative_path = PurePosixPath(info.filename.replace("\\", "/"))
            target_path = (target_root / Path(*relative_path.parts)).resolve()
            if target_root not in target_path.parents:
                raise ValueError(f"Unsicherer Zielpfad im ZIP: {info.filename}")
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info, "r") as src, open(target_path, "wb") as dst:
                dst.write(src.read())
        return len(members)


def _analyze_zip_payload(payload: dict[str, Any], source_kind: str) -> dict[str, Any]:
    filename = _clean_filename(payload.get("filename"), source_kind)
    zip_bytes = _decode_zip_bytes(payload.get("zip_base64"))
    if not zip_bytes:
        raise ValueError("ZIP-Archiv ist leer.")

    with tempfile.TemporaryDirectory(prefix="methodenanalyser-webapp-zip-") as tmpdir:
        extracted_count = _extract_python_zip(zip_bytes, Path(tmpdir))
        result = analyze_project(tmpdir)
        report = build_json_report(source_kind, result, source_name=filename)
        report["source"]["archive_entries"] = extracted_count
        return {
            "ok": True,
            "has_findings": _project_has_findings(result),
            "text_report": generate_project_report(result),
            "report": report,
        }


def analyze_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Analyze browser-submitted Python code and return API-ready JSON."""
    source_kind = payload.get("source_kind", "snippet")
    if source_kind == "zip":
        return _analyze_zip_payload(payload, source_kind)

    code = payload.get("code")
    if not isinstance(code, str) or not code.strip():
        raise ValueError("Python-Code fehlt.")

    if source_kind not in {"snippet", "file"}:
        raise ValueError("source_kind muss 'snippet', 'file' oder 'zip' sein.")

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
    resolved_root = root.resolve()
    normalized_path = relative_path.replace("\\", "/").strip()
    if not normalized_path:
        return None
    relative = PurePosixPath(normalized_path)
    if relative.is_absolute():
        return None
    if any(part in {"", ".", ".."} for part in relative.parts):
        return None
    target = root.joinpath(*relative.parts).resolve()
    try:
        target.relative_to(resolved_root)
    except ValueError:
        return None
    if target == resolved_root:
        return None
    if not target.is_file():
        return None
    return target


def _content_type_for_path(target: Path) -> str:
    return CONTENT_TYPES_BY_SUFFIX.get(target.suffix.lower(), "application/octet-stream")


def _discover_candidate_ipv4_addresses() -> list[str]:
    addresses: set[str] = set()

    for host_name in {socket.gethostname(), socket.getfqdn()}:
        if not host_name:
            continue
        try:
            infos = socket.getaddrinfo(host_name, None, family=socket.AF_INET, type=socket.SOCK_STREAM)
        except socket.gaierror:
            continue
        for info in infos:
            candidate = info[4][0]
            if candidate:
                addresses.add(candidate)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.connect(("8.8.8.8", 80))
            addresses.add(probe.getsockname()[0])
    except OSError:
        pass

    filtered: list[str] = []
    for candidate in sorted(addresses):
        try:
            parsed = ipaddress.ip_address(candidate)
        except ValueError:
            continue
        if parsed.is_loopback or parsed.is_multicast or parsed.is_unspecified:
            continue
        filtered.append(candidate)
    return filtered


def build_runtime_info(
    bind_host: str,
    bind_port: int,
    address_supplier: Any | None = None,
) -> dict[str, Any]:
    host = (bind_host or "127.0.0.1").strip() or "127.0.0.1"
    supplier = address_supplier or _discover_candidate_ipv4_addresses
    local_url = f"http://127.0.0.1:{bind_port}/"

    info: dict[str, Any] = {
        "bind_host": host,
        "bind_port": bind_port,
        "local_url": local_url,
        "local_only": host in LOCAL_ONLY_HOSTS,
        "lan_enabled": host not in LOCAL_ONLY_HOSTS,
        "mobile_ready": host not in LOCAL_ONLY_HOSTS,
        "candidate_urls": [],
        "mobile_command": f"python webapp/server.py --host 0.0.0.0 --port {bind_port}",
        "mobile_notes": {
            "network": "Nur im vertrauenswürdigen WLAN testen: Der lokale HTTP-Server hat keine Authentifizierung und kein TLS. Browser-Analyse bleibt lokal ohne Cloud.",
            "android": "Android: URL in Chrome oder Edge öffnen und bei Bedarf über das Menü als App installieren.",
            "ios": "iPhone/iPad: URL in Safari öffnen und über Teilen > Zum Home-Bildschirm sichern.",
        },
    }

    if host in WILDCARD_HOSTS:
        for candidate in supplier():
            info["candidate_urls"].append(f"http://{candidate}:{bind_port}/")
        return info

    if host not in LOCAL_ONLY_HOSTS:
        info["candidate_urls"].append(f"http://{host}:{bind_port}/")

    return info


def get_runtime_info(server: Any) -> dict[str, Any]:
    runtime_info = getattr(server, "runtime_info", None)
    if isinstance(runtime_info, dict):
        return runtime_info

    host, port = server.server_address[:2]
    return build_runtime_info(str(host), int(port))


class MethodenAnalyserPwaHandler(BaseHTTPRequestHandler):
    server_version = "MethodenAnalyserPWA/0.3"

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/health":
            self._send_json({"ok": True, "service": "methodenanalyser-webapp"})
            return
        if path == "/api/runtime":
            self._send_json({"ok": True, "runtime": get_runtime_info(self.server)})
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
                {"ok": False, "error": "Request ist größer als 2 MB."},
                status=413,
            )
            return

        try:
            raw_body = self.rfile.read(length).decode("utf-8")
            payload = json.loads(raw_body)
            if not isinstance(payload, dict):
                raise ValueError("JSON-Body muss ein Objekt sein.")
            response = analyze_payload(payload)
        except UnicodeDecodeError as exc:
            self._send_json({"ok": False, "error": f"Request-Body ist kein gültiges UTF-8: {exc}"}, status=400)
            return
        except json.JSONDecodeError as exc:
            self._send_json({"ok": False, "error": f"Ungültiges JSON: {exc}"}, status=400)
            return
        except SyntaxError as exc:
            self._send_json({"ok": False, "error": f"Python-Syntaxfehler: {exc}"}, status=422)
            return
        except zipfile.BadZipFile:
            self._send_json({"ok": False, "error": "ZIP-Archiv ist beschädigt oder ungültig."}, status=400)
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

        content_type = _content_type_for_path(target)
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
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self'",
            )
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
    server.runtime_info = build_runtime_info(args.host, args.port)
    url = f"http://{args.host}:{args.port}/"
    print(f"MethodenAnalyser Web/PWA läuft lokal unter {url}")
    if server.runtime_info["candidate_urls"]:
        print("Mobile/WLAN-Testpfade:")
        for candidate in server.runtime_info["candidate_urls"]:
            print(f"  - {candidate}")
        print("Hinweis: LAN-Testmodus nutzt lokales HTTP ohne Authentifizierung oder TLS; nur im vertrauenswürdigen Netz verwenden.")
    elif server.runtime_info["local_only"]:
        print(f"Für Android/iOS im selben WLAN neu starten mit: {server.runtime_info['mobile_command']}")
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
