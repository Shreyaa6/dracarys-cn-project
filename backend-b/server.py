from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class Handler(BaseHTTPRequestHandler):

    def send_json(self, data):
        body = json.dumps(data).encode("utf-8")
        etag = '"dracarys-v1"'

        # Conditional request: client already has current version
        if self.headers.get("If-None-Match") == etag:
            self.send_response(304)
            self.send_header("ETag", etag)
            self.send_header("Cache-Control", "max-age=60")
            self.send_header("X-Backend", "B")
            self.end_headers()
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Backend", "B")
        self.send_header("Cache-Control", "max-age=60")
        self.send_header("ETag", etag)
        self.end_headers()

        self.wfile.write(body)

    def do_HEAD(self):
        if self.path == "/" or self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("X-Backend", "B")
            self.send_header("Cache-Control", "max-age=60")
            self.send_header("ETag", '"dracarys-v1"')
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):

        if self.path == "/":
            self.send_json({
                "message": "Private Network Service",
                "backend": "B"
            })

        elif self.path == "/api/status":
            self.send_json({
                "backend": "B",
                "status": "ok"
            })

        else:
            self.send_response(404)
            self.end_headers()

server = HTTPServer(("0.0.0.0", 3002), Handler)

print("Backend B running on port 3002")
server.serve_forever()
