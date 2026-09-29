# MoMo SMS REST API

Base URL: `http://localhost:8000`
Auth: HTTP Basic Auth — `admin` / `secret123`

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | /transactions | List all |
| GET | /transactions/{id} | Get one |
| POST | /transactions | Create |
| PUT | /transactions/{id} | Update |
| DELETE | /transactions/{id} | Delete |

## Examples

```bash
curl -u admin:secret123 http://localhost:8000/transactions
curl -u admin:secret123 http://localhost:8000/transactions/1
curl -u admin:secret123 -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -d '{"type":"TRANSFER","amount":1000}'
curl -u admin:secret123 -X PUT http://localhost:8000/transactions/1 \
  -H "Content-Type: application/json" \
  -d '{"type":"RECEIVE","amount":2500}'
curl -u admin:secret123 -X DELETE http://localhost:8000/transactions/1
