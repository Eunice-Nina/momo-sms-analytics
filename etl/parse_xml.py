"""Parse MoMo SMS XML into a list of transaction dicts."""

import json
import os
import re
import xml.etree.ElementTree as ET


def parse_amount(body):
    m = re.search(r"([\d,]+)\s*RWF", body or "")
    return int(m.group(1).replace(",", "")) if m else None


def parse_tx_id(body):
    for pat in [r"TxId:\s*(\d+)", r"Financial Transaction Id:\s*(\d+)", r"Transaction Id:\s*(\d+)"]:
        m = re.search(pat, body or "")
        if m:
            return m.group(1)
    return None


def parse_type(body):
    b = (body or "").lower()
    if "one-time password" in b or "otp" in b:
        return "OTP"
    if "reversal" in b or "reversed" in b:
        return "REVERSAL"
    if "has failed" in b or " failed at " in b:
        return "FAILED"
    if "bank deposit" in b:
        return "DEPOSIT"
    if "withdrawn" in b:
        return "WITHDRAW"
    if "you have received" in b:
        return "RECEIVE"
    if "transferred to" in b:
        return "TRANSFER"
    if "airtime" in b:
        return "AIRTIME"
    if "cash power" in b:
        return "CASH_POWER"
    if "bundles and packs" in b:
        return "BUNDLES"
    if "payment of" in b:
        return "PAYMENT"
    if "transaction of" in b:
        return "MERCHANT_PAYMENT"
    return "UNKNOWN"


def parse_timestamp(body):
    m = re.search(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})", body or "")
    return m.group(1) if m else None


def parse_sender(body):
    b = body or ""
    m = re.search(r"from\s+([A-Za-z][A-Za-z .'\-]+?)\s*\(", b)
    if m:
        return m.group(1).strip()
    m = re.search(r"by\s+([A-Za-z0-9 &.,'\-]+?)\s+on your MOMO", b, re.I)
    if m:
        return m.group(1).strip()
    return None


def parse_receiver(body):
    b = body or ""
    m = re.search(r"transferred to\s+([A-Za-z][A-Za-z .'\-]+?)\s*\(", b)
    if m:
        return m.group(1).strip()
    m = re.search(r"payment of\s*[\d,]+\s*RWF\s+to\s+([A-Za-z][A-Za-z .'\-]+?)\s+\d+", b)
    if m:
        return m.group(1).strip()
    m = re.search(r"payment of\s*[\d,]+\s*RWF\s+to\s+([A-Za-z][A-Za-z .'\-]+?)\s+with", b)
    if m:
        return m.group(1).strip()
    return None


def parse_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    records = []
    for idx, sms in enumerate(root.findall("sms"), start=1):
        a = dict(sms.attrib)
        body = a.get("body", "")
        records.append({
            "id": idx,
            "sms_address": a.get("address"),
            "sms_date_ms": int(a["date"]) if a.get("date") else None,
            "sms_readable_date": a.get("readable_date"),
            "transaction_id": parse_tx_id(body),
            "type": parse_type(body),
            "amount": parse_amount(body),
            "sender": parse_sender(body),
            "receiver": parse_receiver(body),
            "timestamp": parse_timestamp(body),
            "body": body,
        })
    return records


def load_or_parse_transactions(xml_path, json_path):
    if os.path.exists(json_path):
        with open(json_path, encoding="utf-8") as f:
            return json.load(f)
    records = parse_xml(xml_path)
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    return records
