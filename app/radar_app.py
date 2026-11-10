"""Tiny "radar console" web app for the Jenkins + Selenium lab.

Standard library only, so it runs anywhere Python 3 runs.

  GET  /login        HTML login page (the Selenium tests drive this)
  GET  /api/health   {"status": "ok"}
  GET  /api/tracks   list of radar tracks (the API tests check its schema)
  POST /api/login    {"username": ..., "password": ...} -> 200 + token, or 401

Run it by itself to look at it in a browser:
  python3 app/radar_app.py --port 5050      then open http://127.0.0.1:5050/login
"""
import argparse
import json
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Lab-only demo account. Not a real credential.
USERS = {"operator": "radar123"}

TRACKS = [
    {"id": 1, "range_m": 1250.0, "azimuth_deg": 42.5, "velocity_mps": 14.2, "classification": "drone"},
    {"id": 2, "range_m": 3400.0, "azimuth_deg": 310.0, "velocity_mps": 27.8, "classification": "vehicle"},
    {"id": 3, "range_m": 610.0, "azimuth_deg": 95.0, "velocity_mps": 1.3, "classification": "person"},
]

# The page waits a RANDOM 300-1800 ms before showing the result, the way a real
# UI lags behind the network. A fixed time.sleep(1) in a test will pass some runs
# and fail others; an explicit wait passes every time. That is the whole lesson.
LOGIN_PAGE = """<!doctype html>
<html>
<head><meta charset="utf-8"><title>Radar Console Login</title></head>
<body>
  <h1>Radar Console</h1>
  <form id="login-form">
    <label>Username <input id="username" name="username" autocomplete="off"></label>
    <label>Password <input id="password" name="password" type="password"></label>
    <button id="login-btn" type="submit">Sign in</button>
  </form>
  <p id="status"></p>
  <div id="welcome" hidden></div>
  <p id="error" hidden></p>
  <script>
    document.getElementById("login-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const status = document.getElementById("status");
      const welcome = document.getElementById("welcome");
      const error = document.getElementById("error");
      status.textContent = "Signing in...";
      welcome.hidden = true;
      error.hidden = true;
      const res = await fetch("/api/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          username: document.getElementById("username").value,
          password: document.getElementById("password").value,
        }),
      });
      const data = await res.json();
      const delayMs = 300 + Math.floor(Math.random() * 1500);
      setTimeout(async () => {
        status.textContent = "";
        if (res.ok) {
          const tracks = await (await fetch("/api/tracks")).json();
          welcome.textContent = `Welcome, ${data.username}. ${tracks.length} active tracks.`;
          welcome.hidden = false;
        } else {
          error.textContent = data.error;
          error.hidden = false;
        }
      }, delayMs);
    });
  </script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, content_type="application/json"):
        payload = body.encode() if isinstance(body, str) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path in ("/", "/login"):
            self._send(200, LOGIN_PAGE, "text/html; charset=utf-8")
        elif self.path == "/api/health":
            self._send(200, {"status": "ok"})
        elif self.path == "/api/tracks":
            self._send(200, TRACKS)
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/api/login":
            self._send(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            self._send(400, {"error": "body must be JSON"})
            return
        user, password = body.get("username", ""), body.get("password", "")
        if not user or not password:
            self._send(400, {"error": "username and password are required"})
        elif USERS.get(user) == password:
            self._send(200, {"username": user, "token": secrets.token_hex(8)})
        else:
            self._send(401, {"error": "Invalid username or password"})

    def log_message(self, fmt, *args):
        pass  # keep pytest output clean


def make_server(host="127.0.0.1", port=0):
    """port=0 lets the OS pick a free port (what the tests use)."""
    return ThreadingHTTPServer((host, port), Handler)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the radar console demo app")
    parser.add_argument("--port", type=int, default=5050)
    args = parser.parse_args()
    server = make_server(port=args.port)
    print(f"Radar console running at http://127.0.0.1:{args.port}/login  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
