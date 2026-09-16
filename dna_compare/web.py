from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from webbrowser import open as open_browser

from dna_compare.config import SAMPLE_DIR, UPLOAD_DIR, default_settings
from dna_compare.report import STATIC_DIR
from dna_compare.service import AnalysisService

MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
}


def _truthy(value: str | None, default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off"}


class AnalyzeHandler(BaseHTTPRequestHandler):
    server_version = "DnaCompare/1.0"

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} - {fmt % args}")

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/index.html"}:
            self._send_file(STATIC_DIR / "index.html")
            return
        if parsed.path.startswith("/static/"):
            name = Path(parsed.path).name
            path = STATIC_DIR / name
            if path.is_file() and path.resolve().parent == STATIC_DIR.resolve():
                self._send_file(path)
                return
            self._json(404, {"error": "not found"})
            return
        if parsed.path == "/api/samples":
            names = sorted(
                p.name
                for p in SAMPLE_DIR.iterdir()
                if p.is_file() and (p.suffix == ".vcf" or p.name.endswith(".vcf.gz"))
            )
            self._json(200, {"samples": names})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else b""
        if parsed.path == "/api/analyze":
            filename = self.headers.get("X-Filename") or "upload.vcf"
            filename = Path(filename).name
            query = parse_qs(parsed.query)
            flags = {
                "compare_hominin_flag": _truthy((query.get("hominin") or ["true"])[0]),
                "compare_caste_flag": _truthy((query.get("caste") or ["true"])[0]),
                "compare_populations_flag": _truthy((query.get("populations") or ["true"])[0]),
                "compare_ancestry_flag": _truthy((query.get("ancestry") or ["true"])[0]),
                "compare_haplogroups_flag": _truthy((query.get("haplogroups") or ["true"])[0]),
            }
            UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
            dest = UPLOAD_DIR / filename
            dest.write_bytes(body)
            payload = AnalysisService(default_settings()).analyze(dest, filename=filename, **flags).to_dict()
            self._json(200 if payload["ok"] else 400, payload)
            return
        if parsed.path == "/api/analyze-sample":
            try:
                data = json.loads(body.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                self._json(400, {"error": "invalid json"})
                return
            name = Path(str(data.get("filename") or "")).name
            path = SAMPLE_DIR / name
            if not name or not path.is_file() or path.resolve().parent != SAMPLE_DIR.resolve():
                self._json(400, {"error": "unknown sample"})
                return
            flags = {
                "compare_hominin_flag": _truthy(str(data.get("hominin", True))),
                "compare_caste_flag": _truthy(str(data.get("caste", True))),
                "compare_populations_flag": _truthy(str(data.get("populations", True))),
                "compare_ancestry_flag": _truthy(str(data.get("ancestry", True))),
                "compare_haplogroups_flag": _truthy(str(data.get("haplogroups", True))),
            }
            payload = AnalysisService(default_settings()).analyze(path, filename=name, **flags).to_dict()
            self._json(200 if payload["ok"] else 400, payload)
            return
        self._json(404, {"error": "not found"})

    def _send_file(self, path: Path) -> None:
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", MIME.get(path.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json(self, status: int, payload: dict) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def serve(host: str = "127.0.0.1", port: int = 8765, open_browser_tab: bool = True) -> None:
    httpd = ThreadingHTTPServer((host, port), AnalyzeHandler)
    url = f"http://{host}:{port}/"
    print(f"Dashboard at {url}", flush=True)
    if open_browser_tab:
        open_browser(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping.")
        httpd.shutdown()
