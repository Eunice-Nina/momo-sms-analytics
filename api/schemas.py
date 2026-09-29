"""Field definitions for a transaction record."""

TRANSACTION_FIELDS = [
    "id",
    "type",
    "amount",
    "sender",
    "receiver",
    "timestamp",
    "transaction_id",
    "sms_readable_date",
    "body",
]

REQUIRED_FOR_CREATE = ("type", "amount")
