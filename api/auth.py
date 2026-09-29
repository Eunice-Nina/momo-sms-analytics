"""HTTP Basic Authentication."""

import base64
import os

USERS = {
    os.getenv("API_USER", "admin"): os.getenv("API_PASS", "secret123"),
}


def is_authorized(auth_header):
    """Return True if Authorization header carries valid Basic credentials."""
    if not auth_header or not auth_header.startswith("Basic "):
        return False
    try:
        decoded = base64.b64decode(auth_header[6:]).decode("utf-8")
        username, password = decoded.split(":", 1)
    except Exception:
        return False
    expected = USERS.get(username)
    if expected is None:
        return False
    return expected == password
