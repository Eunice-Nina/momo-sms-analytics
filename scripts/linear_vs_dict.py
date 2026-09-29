"""DSA: compare linear search vs dictionary lookup on transaction records."""

import json
import os
import timeit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_FILE = os.path.join(ROOT, "data", "transactions.json")


def linear_search(records, target_id):
    for rec in records:
        if rec.get("id") == target_id:
            return rec
    return None


def dict_lookup(index, target_id):
    return index.get(target_id)


def main():
    with open(JSON_FILE, encoding="utf-8") as f:
        records = json.load(f)

    sample = records[:20]
    index = {r["id"]: r for r in sample}
    target = sample[-1]["id"]
    runs = 10000

    t_linear = timeit.timeit(lambda: linear_search(sample, target), number=runs)
    t_dict = timeit.timeit(lambda: dict_lookup(index, target), number=runs)

    print(f"Records in test: {len(sample)}")
    print(f"Target ID: {target}")
    print(f"Linear search : {t_linear:.6f}s for {runs} runs")
    print(f"Dict lookup   : {t_dict:.6f}s for {runs} runs")
    if t_dict > 0:
        print(f"Dictionary is {t_linear / t_dict:.1f}x faster in this test")
    print()
    print("Why dictionary is faster: O(n) scan vs O(1) average hash lookup.")
    print("Alternatives: database B-tree index, balanced BST, binary search on sorted list.")


if __name__ == "__main__":
    main()
