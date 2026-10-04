#!/usr/bin/env python3
"""
Backend B Server - Team Dracarys
Host: Raspberry Pi (10.7.23.235)
Interface: wlan0
Port: 3002
Source Path: ~/CN_Project/backend-b/server.py
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json

HOST = "0.0.0.0"
PORT = 3002
BACKEND_ID = "B"
ETAG_VALUE = '"dracarys-v1"'
CACHE_CONTROL = "max-age=60"


class BackendBHandler(BaseHTTPRequestHandler):
    server_version = "DracarysBackend/1.0"

    def _get_response_payload(self):
        """Returns (status_code, body_bytes, content_type) based on path."""
        if self.path == "/":
            payload = {
                "message": "Private Network Service",
                "backend": BACKEND_ID
            }
            body = (json.dumps(payload, indent=2) + "\n").encode("utf-8")
            return 200, body, "application/json"
        elif self.path == "/api/status":
            payload = {
                "backend": BACKEND_ID,
                "status": "ok"
            }
            body = (json.dumps(payload, indent=2) + "\n").encode("utf-8")
            return 200, body, "application/json"
        else:
            payload = {
                "error": "Not Found",
                "backend": BACKEND_ID,
                "path": self.path
            }
            body = (json.dumps(payload, indent=2) + "\n").encode("utf-8")
            return 404, body, "application/json"

    def _check_etag_match(self):
        """Checks if the client provided an If-None-Match matching our ETag."""
        if_none_match = self.headers.get("If-None-Match")
        if not if_none_match:
            return False
        # Normalize and compare (support quoted, unquoted, or wildcard)
        cleaned = if_none_match.strip()
        return cleaned in (ETAG_VALUE, ETAG_VALUE.strip('"'), "*")

    def _send_common_headers(self, status_code, content_type=None, content_length=None):
        self.send_response(status_code)
        self.send_header("X-Backend", BACKEND_ID)
        self.send_header("ETag", ETAG_VALUE)
        self.send_header("Cache-Control", CACHE_CONTROL)
        if content_type:
            self.send_header("Content-Type", content_type)
        if content_length is not None:
            self.send_header("Content-Length", str(content_length))
        self.end_headers()

    def do_HEAD(self):
        status_code, body, content_type = self._get_response_payload()
        if status_code == 200 and self._check_etag_match():
            self._send_common_headers(304)
            return

        self._send_common_headers(
            status_code=status_code,
            content_type=content_type,
            content_length=len(body)
        )

    def do_GET(self):
        status_code, body, content_type = self._get_response_payload()
        if status_code == 200 and self._check_etag_match():
            self._send_common_headers(304)
            return

        self._send_common_headers(
            status_code=status_code,
            content_type=content_type,
            content_length=len(body)
        )
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Clean logging format for evaluator clarity
        print(f"[{BACKEND_ID}] {self.address_string()} - - [{self.log_date_time_string()}] {format % args}")


def run():
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, BackendBHandler)
    print(f"Starting Backend {BACKEND_ID} HTTP server on {HOST}:{PORT}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\nStopping Backend {BACKEND_ID} HTTP server.")
        httpd.server_close()


if __name__ == "__main__":
    run()
