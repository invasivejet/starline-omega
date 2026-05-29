#!/usr/bin/env python3
"""Local telemetry sink — POST JSON lines for Studio/headless field research.

  python scripts/telemetry_server.py --port 8765

Roblox (published or Studio with HTTP enabled):
  set STARLINE_TELEMETRY_URL=http://localhost:8765/telemetry
"""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


class Handler(BaseHTTPRequestHandler):
    log_path: Path = Path("output/telemetry_live.jsonl")

    def log_message(self, fmt: str, *args) -> None:
        pass

    def do_POST(self) -> None:
        if self.path not in ("/telemetry", "/telemetry/"):
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_error(400, "invalid json")
            return
        Handler.log_path.parent.mkdir(parents=True, exist_ok=True)
        with Handler.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
        self.send_response(204)
        self.end_headers()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--out", default="output/telemetry_live.jsonl")
    args = ap.parse_args()
    Handler.log_path = Path(args.out)
    server = HTTPServer(("127.0.0.1", args.port), Handler)
    print(f"[telemetry] http://127.0.0.1:{args.port}/telemetry → {args.out}")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
