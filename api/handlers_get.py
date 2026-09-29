def handle_get_all(store):
    return 200, store.all()


def handle_get_one(store, tx_id):
    record = store.get(tx_id)
    if record is None:
        return 404, {"error": "Transaction not found", "id": tx_id}
    return 200, record
