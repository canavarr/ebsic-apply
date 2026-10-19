#!/usr/bin/env python3
"""
Local server for the event back office.

Serves the site exactly like `python3 -m http.server`, and adds one extra
endpoint the admin page posts to:

    POST /api/events   ->  writes events/events.json

Without this server the site still works and the back office still works — it
just falls back to downloading events.json for you to drop in by hand, because
a plain static server cannot accept writes.

    python3 serve-admin.py            # http://127.0.0.1:8777
    python3 serve-admin.py --port 9000

Binds to 127.0.0.1 only. The endpoint has no authentication, so it is a local
editing tool, not something to expose on a network or deploy.
"""

import argparse
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "events" / "events.json"
MAX_BODY = 1_000_000  # 1 MB is far more than a calendar needs

REQUIRED = ("title", "start")
ALLOWED = {"id", "title", "kind", "start", "end", "location", "url", "urlLabel", "blurb", "tbc"}


def validate(payload):
    """Return (events, error). Rejects anything that isn't a sane event list."""
    if not isinstance(payload, dict):
        return None, "body must be a JSON object"
    events = payload.get("events")
    if not isinstance(events, list):
        return None, "'events' must be a list"
    if len(events) > 500:
        return None, "too many events"

    cleaned = []
    for i, ev in enumerate(events):
        if not isinstance(ev, dict):
            return None, f"event {i} is not an object"
        unknown = set(ev) - ALLOWED
        if unknown:
            return None, f"event {i} has unexpected fields: {', '.join(sorted(unknown))}"
        for field in REQUIRED:
            if not str(ev.get(field, "")).strip():
                return None, f"event {i} is missing {field}"
        # Normalise: keep only known fields, coerce types predictably.
        cleaned.append({
            "id": str(ev.get("id") or f"event-{i}"),
            "title": str(ev["title"]).strip(),
            "kind": str(ev.get("kind", "")).strip(),
            "start": str(ev["start"]).strip(),
            "end": str(ev.get("end", "")).strip(),
            "location": str(ev.get("location", "")).strip(),
            "url": str(ev.get("url", "")).strip(),
            "urlLabel": str(ev.get("urlLabel", "")).strip(),
            "blurb": str(ev.get("blurb", "")).strip(),
            "tbc": bool(ev.get("tbc", False)),
        })
    return cleaned, None


def write_atomically(path, data):
    """Write via a temp file in the same directory, then replace.

    A half-written calendar is worse than an unchanged one, and the page reads
    this file on every load.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


class Handler(SimpleHTTPRequestHandler):
    def _json(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path.split("?")[0] != "/api/events":
            return self._json(404, {"ok": False, "error": "unknown endpoint"})

        # Local tool: refuse anything that didn't come from this machine.
        if self.client_address[0] not in ("127.0.0.1", "::1"):
            return self._json(403, {"ok": False, "error": "local requests only"})

        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return self._json(400, {"ok": False, "error": "bad Content-Length"})
        if length <= 0 or length > MAX_BODY:
            return self._json(413, {"ok": False, "error": "body missing or too large"})

        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception as e:
            return self._json(400, {"ok": False, "error": f"invalid JSON: {e}"})

        events, err = validate(payload)
        if err:
            return self._json(422, {"ok": False, "error": err})

        # Keep one rolling backup so a bad save is recoverable.
        if TARGET.exists():
            shutil.copy2(TARGET, TARGET.with_suffix(".json.bak"))

        doc = {"updated": datetime.now(timezone.utc).isoformat(timespec="seconds"), "events": events}
        try:
            write_atomically(TARGET, doc)
        except Exception as e:
            return self._json(500, {"ok": False, "error": f"could not write: {e}"})

        print(f"  saved {len(events)} event(s) -> {TARGET.relative_to(ROOT)}")
        return self._json(200, {"ok": True, "count": len(events), "updated": doc["updated"]})

    def end_headers(self):
        # The admin page must never read a stale calendar.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        if "api/events" in (args[0] if args else ""):
            super().log_message(fmt, *args)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8777)
    args = ap.parse_args()

    handler = partial(Handler, directory=str(ROOT))
    with ThreadingHTTPServer(("127.0.0.1", args.port), handler) as httpd:
        print(f"  site       http://127.0.0.1:{args.port}/")
        print(f"  back office http://127.0.0.1:{args.port}/admin/")
        print(f"  writes     {TARGET.relative_to(ROOT)}")
        print("  ctrl-c to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  stopped")
            return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
