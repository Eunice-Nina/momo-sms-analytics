"""Plain http.server REST API for MoMo SMS with Basic Auth.

Run:
    python api/app.py
"""

import json
import os
import re
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(_file_)))
sys.path.insert(0, ROOT)

from api.auth import is_authorized
from api.handlers_get import handle_get_all, handle_get_one
from api.handlers_write import handle_post, handle_put, handle_delete
from api.storage import TransactionStore
from etl.parse_xml import load_or_parse_transactions

XML_CANDIDATES = [
    os.path.join(ROOT, "data", "modified_sms_v2-1.xml"),
    os.path.join(ROOT, "data", "modified_sms_v2.xml"),
    os.path.join(ROOT, "modified_sms_v2-1.xml"),
    os.path.join(ROOT, "modified_sms_v2.xml"),
]
DATA_JSON = os.path.join(ROOT, "data", "transactions.json")


class Handler(BaseHTTPRequestHandler):
    store = None
    lock = threading.Lock()

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - - [%s] %s\n" % (
            self.address_string(),
            self.log_date_time_string(),
            fmt % args,
        ))

    def send_json(self, code, payload, extra_headers=None):
        body = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def send_unauthorized(self):
        self.send_json(
            401,
            {"error": "Unauthorized", "message": "Invalid or missing credentials"},
            {"WWW-Authenticate": 'Basic realm="MoMo API"'},
        )

    def require_auth(self):
        if not is_authorized(self.headers.get("Authorization", "")):
            self.send_unauthorized()
            return False
        return True

    def read_json_body(self):
        n = int(self.headers.get("Content-Length", 0))
        if n == 0:
            return {}
        return json.loads(self.rfile.read(n).decode("utf-8"))

    def tx_id_from_path(self):
        path = urlparse(self.path).path
        m = re.fullmatch(r"/transactions/(\d+)", path)
        return int(m.group(1)) if m else None

    def do_GET(self):
        if not self.require_auth():
            return
        path = urlparse(self.path).path
        if path == "/transactions":
            code, payload = handle_get_all(self.store)
            return self.send_json(code, payload)
        tid = self.tx_id_from_path()
        if tid is not None:
            code, payload = handle_get_one(self.store, tid)
            return self.send_json(code, payload)
        return self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        if not self.require_auth():
            return
        if urlparse(self.path).path != "/transactions":
            return self.send_json(404, {"error": "Not found"})
        try:
            data = self.read_json_body()
        except Exception:
            return self.send_json(400, {"error": "Invalid JSON"})
        with self.lock:
            code, payload = handle_post(self.store, data)
        return self.send_json(code, payload)

    def do_PUT(self):
        if not self.require_auth():
            return
        tid = self.tx_id_from_path()
        if tid is None:
            return self.send_json(404, {"error": "Not found"})
        try:
            data = self.read_json_body()
        except Exception:
            return self.send_json(400, {"error": "Invalid JSON"})
        with self.lock:
            code, payload = handle_put(self.store, tid, data)
        return self.send_json(code, payload)

    def do_DELETE(self):
        if not self.require_auth():
            return
        tid = self.tx_id_from_path()
        if tid is None:
            return self.send_json(404, {"error": "Not found"})
        with self.lock:
            code, payload = handle_delete(self.store, tid)
        return self.send_json(code, payload)


def main():
    xml = next((p for p in XML_CANDIDATES if os.path.exists(p)), None)
    if xml is None:
        print("XML not found. Put modified_sms_v2.xml in ./data/ or repo root.")
        sys.exit(1)

    records = load_or_parse_transactions(xml, DATA_JSON)
    Handler.store = TransactionStore(records)

    port = int(os.getenv("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Loaded {len(records)} transactions from {xml}")
    print(f"Serving on http://localhost:{port}")
    print("Default credentials: admin / secret123")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()


if _name_ == "_main_":
    main()
