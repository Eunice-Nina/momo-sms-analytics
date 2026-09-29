from api.schemas import REQUIRED_FOR_CREATE


def validate(data):
    if not isinstance(data, dict):
        return "Body must be a JSON object"
    for f in REQUIRED_FOR_CREATE:
        if f not in data:
            return f"Missing required field: {f}"
    if not isinstance(data["amount"], (int, float)):
        return "Field 'amount' must be a number"
    if not isinstance(data["type"], str) or not data["type"]:
        return "Field 'type' must be a non-empty string"
    return None


def handle_post(store, data):
    err = validate(data)
    if err:
        return 400, {"error": err}
    return 201, store.create(data)


def handle_put(store, tx_id, data):
    err = validate(data)
    if err:
        return 400, {"error": err}
    record = store.update(tx_id, data)
    if record is None:
        return 404, {"error": "Transaction not found", "id": tx_id}
    return 200, record


def handle_delete(store, tx_id):
    ok = store.delete(tx_id)
    if not ok:
        return 404, {"error": "Transaction not found", "id": tx_id}
    return 200, {"message": "Transaction deleted", "id": tx_id}
