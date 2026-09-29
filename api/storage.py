"""In-memory transaction store with O(1) id lookup."""

import threading


class TransactionStore:
    def __init__(self, records):
        self._lock = threading.Lock()
        self._records = list(records)
        self._index = {r["id"]: r for r in self._records}
        self._next_id = max(self._index.keys(), default=0) + 1

    def all(self):
        return list(self._records)

    def get(self, tx_id):
        return self._index.get(tx_id)

    def create(self, data):
        with self._lock:
            new_id = self._next_id
            self._next_id += 1
            record = dict(data)
            record["id"] = new_id
            self._records.append(record)
            self._index[new_id] = record
            return record

    def update(self, tx_id, data):
        with self._lock:
            if tx_id not in self._index:
                return None
            record = dict(data)
            record["id"] = tx_id
            for i, r in enumerate(self._records):
                if r["id"] == tx_id:
                    self._records[i] = record
                    break
            self._index[tx_id] = record
            return record

    def delete(self, tx_id):
        with self._lock:
            if tx_id not in self._index:
                return False
            del self._index[tx_id]
            self._records[:] = [r for r in self._records if r["id"] != tx_id]
            return True

    def count(self):
        return len(self._records)