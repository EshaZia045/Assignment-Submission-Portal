from http.server import BaseHTTPRequestHandler, HTTPServer
import json, os

TOKEN = os.environ.get("REPORT_TOKEN", "")

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/report":
            return self.send_error(404)
        if TOKEN and self.headers.get("X-Report-Token") != TOKEN:
            return self.send_error(401)
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        try:
            data = json.loads(body)
        except ValueError:
            return self.send_error(400)
        with open("test-report.json", "w") as f:
            json.dump(data, f, indent=2)
        print("Saved report for commit", data.get("commit_sha"),
              "-", data.get("overall_status"))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"saved")

if __name__ == "__main__":
    print("Receiver listening on http://127.0.0.1:5001/report")
    HTTPServer(("127.0.0.1", 5001), Handler).serve_forever()
