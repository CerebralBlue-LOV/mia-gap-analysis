#!/usr/bin/env python3
"""Tiny static server + NeuralSeek API proxy for MiAcademy Gap Analysis.

Serves the static UI and proxies POST /api/* to the NeuralSeek public API,
injecting the apikey header server-side so the browser never sees the credential.
"""
import base64
import hmac
import http.server
import json
import os
import subprocess
import sys
import threading

PORT = int(os.environ.get("PORT", "8080"))
HOST = os.environ.get("HOST", "127.0.0.1")
API_KEY = os.environ.get("NEURALSEEK_API_KEY", "")
PUBLIC_URL = os.environ.get("NEURALSEEK_PUBLIC_API_URL", "")
BASIC_AUTH_USER = os.environ.get("BASIC_AUTH_USER", "")
BASIC_AUTH_PASS = os.environ.get("BASIC_AUTH_PASS", "")
AUTH_ENABLED = bool(BASIC_AUTH_USER and BASIC_AUTH_PASS)

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def log_message(self, fmt, *args):
        sys.stdout.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))
        sys.stdout.flush()

    def _check_auth(self):
        if not AUTH_ENABLED:
            return True
        header = self.headers.get("Authorization", "")
        if header.startswith("Basic "):
            try:
                decoded = base64.b64decode(header[6:]).decode("utf-8", "replace")
                user, _, pw = decoded.partition(":")
                if hmac.compare_digest(user, BASIC_AUTH_USER) and hmac.compare_digest(pw, BASIC_AUTH_PASS):
                    return True
            except Exception:
                pass
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="MiAcademy Gap Analysis"')
        self.send_header("Content-Length", "0")
        self.end_headers()
        return False

    def do_GET(self):
        if not self._check_auth():
            return
        return super().do_GET()

    def do_POST(self):
        if not self._check_auth():
            return
        if self.path.startswith("/api/"):
            return self._proxy()
        self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _proxy(self):
        if not API_KEY or not PUBLIC_URL:
            self.send_error(500, "Missing NEURALSEEK_API_KEY or NEURALSEEK_PUBLIC_API_URL")
            return
        target_path = self.path[len("/api"):]
        target = PUBLIC_URL.rstrip("/") + target_path
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else b""
        try:
            result = subprocess.run(
                [
                    "curl", "-s", "-w", "\n%{http_code}",
                    "-X", "POST", target,
                    "-H", f"apikey: {API_KEY}",
                    "-H", "Content-Type: application/json",
                    "--data-binary", "@-",
                    "--max-time", "600",
                ],
                input=body,
                capture_output=True,
                timeout=620,
            )
            out = result.stdout
            sep = out.rfind(b"\n")
            status_code = int(out[sep + 1:].strip() or b"500")
            payload = out[:sep] if sep >= 0 else out
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        except Exception as e:
            self.send_error(502, f"Proxy error: {e}")


def main():
    if not API_KEY or not PUBLIC_URL:
        print("WARNING: NEURALSEEK_API_KEY / NEURALSEEK_PUBLIC_API_URL not set; /api proxy will fail.")
    if HOST != "127.0.0.1" and not AUTH_ENABLED:
        print("ERROR: Refusing to bind to a public interface without BASIC_AUTH_USER/BASIC_AUTH_PASS set.")
        sys.exit(1)
    if AUTH_ENABLED:
        print("Basic Auth enabled.")
    http.server.ThreadingHTTPServer.allow_reuse_address = True
    http.server.ThreadingHTTPServer.daemon_threads = True
    with http.server.ThreadingHTTPServer((HOST, PORT), Handler) as httpd:
        print(f"MiAcademy Gap Analysis ready at http://{HOST}:{PORT}/")
        sys.stdout.flush()
        httpd.serve_forever()


if __name__ == "__main__":
    main()
