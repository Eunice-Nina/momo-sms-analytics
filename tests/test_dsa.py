import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from scripts.linear_vs_dict import linear_search, dict_lookup


def data():
    records = [{"id": i, "type": "X"} for i in range(1, 21)]
    return records, {r["id"]: r for r in records}


def test_linear():
    recs, _ = data()
    assert linear_search(recs, 20)["id"] == 20
    assert linear_search(recs, 999) is None


def test_dict():
    _, idx = data()
    assert dict_lookup(idx, 20)["id"] == 20
    assert dict_lookup(idx, 999) is None


if __name__ == "__main__":
    test_linear()
    test_dict()
    print("DSA tests passed")
