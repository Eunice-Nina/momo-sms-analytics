import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from api.storage import TransactionStore
from api.handlers_get import handle_get_all, handle_get_one
from api.handlers_write import handle_post, handle_put, handle_delete


def make():
    return TransactionStore([{"id": 1, "type": "RECEIVE", "amount": 100}])


def test_get_all():
    code, payload = handle_get_all(make())
    assert code == 200 and len(payload) == 1


def test_get_one():
    code, payload = handle_get_one(make(), 1)
    assert code == 200 and payload["amount"] == 100


def test_get_missing():
    code, _ = handle_get_one(make(), 999)
    assert code == 404


def test_post():
    s = make()
    code, payload = handle_post(s, {"type": "TRANSFER", "amount": 500})
    assert code == 201 and payload["id"] == 2


def test_post_missing():
    code, _ = handle_post(make(), {"type": "TRANSFER"})
    assert code == 400


def test_put():
    s = make()
    code, payload = handle_put(s, 1, {"type": "TRANSFER", "amount": 900})
    assert code == 200 and s.get(1)["amount"] == 900


def test_delete():
    s = make()
    code, _ = handle_delete(s, 1)
    assert code == 200 and s.get(1) is None


def test_delete_missing():
    code, _ = handle_delete(make(), 999)
    assert code == 404


if __name__ == "__main__":
    test_get_all(); test_get_one(); test_get_missing()
    test_post(); test_post_missing()
    test_put(); test_delete(); test_delete_missing()
    print("Handler tests passed")
