"""Run the ETL: parse XML -> data/transactions.json."""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from etl.parse_xml import parse_xml

XML_CANDIDATES = [
    os.path.join(ROOT, "data", "modified_sms_v2-1.xml"),
    os.path.join(ROOT, "data", "modified_sms_v2.xml"),
    os.path.join(ROOT, "modified_sms_v2-1.xml"),
    os.path.join(ROOT, "modified_sms_v2.xml"),
]
OUT = os.path.join(ROOT, "data", "transactions.json")


def main():
    xml = next((p for p in XML_CANDIDATES if os.path.exists(p)), None)
    if xml is None:
        print("XML file not found. Put modified_sms_v2.xml in ./data/ or repo root.")
        sys.exit(1)
    records = parse_xml(xml)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f"Parsed {len(records)} records from {xml}")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()