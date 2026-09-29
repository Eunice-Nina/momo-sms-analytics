#!/usr/bin/env bash
BASE="http://localhost:8000"
AUTH="admin:secret123"

echo "== GET all =="
curl -s -u "$AUTH" "$BASE/transactions" | head -n 20; echo
echo "== GET one =="
curl -s -u "$AUTH" "$BASE/transactions/1"; echo
echo "== Unauthorized =="
curl -i -s -u admin:wrong "$BASE/transactions" | head -n 5; echo
echo "== POST =="
curl -s -u "$AUTH" -X POST "$BASE/transactions" -H "Content-Type: application/json" \
  -d '{"type":"TRANSFER","amount":1000,"sender":"Alice","receiver":"Bob"}'; echo
echo "== PUT =="
curl -s -u "$AUTH" -X PUT "$BASE/transactions/1" -H "Content-Type: application/json" \
  -d '{"type":"RECEIVE","amount":2500,"sender":"Jane Smith"}'; echo
echo "== DELETE =="
curl -s -u "$AUTH" -X DELETE "$BASE/transactions/1"; echo
