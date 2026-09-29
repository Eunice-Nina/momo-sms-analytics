import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from etl.parse_xml import parse_xml, parse_amount, parse_tx_id, parse_type

CANDIDATES = [
    os.path.join(ROOT, "data", "modified_sms_v2-1.xml"),
    os.path.join(ROOT, "data", "modified_sms_v2.xml"),
    os.path.join(ROOT, "modified_sms_v2-1.xml"),
    os.path.join(ROOT, "modified_sms_v2.xml"),
]
XML = next((p for p in CANDIDATES if os.path.exists(p)), None)


def test_amount():
    assert parse_amount("You have received 2000 RWF from Jane") == 2000
    assert parse_amount("payment of 10,900 RWF to Jane") == 10900
    assert parse_amount("nothing") is None


def test_tx_id():
    assert parse_tx_id("TxId: 73214484437. Your payment") == "73214484437"
    assert parse_tx_id("Financial Transaction Id: 76662021700.") == "76662021700"
    assert parse_tx_id("no id") is None


def test_type():
    assert parse_type("You have received 2000 RWF") == "RECEIVE"
    assert parse_type("Your payment of 1,000 RWF to Jane") == "PAYMENT"
    assert parse_type("has been reversed") == "REVERSAL"
    assert parse_type("one-time password is :2476") == "OTP"


def test_parse_xml():
    assert XML is not None, "XML file not found"
    records = parse_xml(XML)
    assert len(records) > 0
    for key in ("id", "type", "body", "sms_address"):
        assert key in records[0]
    assert [r["id"] for r in records] == list(range(1, len(records) + 1))


if __name__ == "__main__":
    test_amount()
    test_tx_id()
    test_type()
    test_parse_xml()
    print("Parser tests passed")
