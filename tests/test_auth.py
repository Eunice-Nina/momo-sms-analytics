import base64
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from api.auth import is_authorized


def header(u, p):
    return "Basic " + base64.b64encode(f"{u}:{p}".encode()).decode()


def test_valid():
    assert is_authorized(header("admin", "secret123")) is True


def test_bad_password():
    assert is_authorized(header("admin", "wrong")) is False


def test_bad_user():
    assert is_authorized(header("nobody", "secret123")) is False


def test_missing():
    assert is_authorized("") is False


def test_malformed():
    assert is_authorized("Bearer abc") is False
    assert is_authorized("Basic !!!notbase64!!!") is False


if __name__ == "__main__":
    test_valid()
    test_bad_password()
    test_bad_user()
    test_missing()
    test_malformed()
    print("Auth tests passed")
