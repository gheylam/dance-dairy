# squirtle — app
Greenfield discovery UI. Stub-first: hardcoded data, no DB yet.

Run (from `squirtle/`):

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Routes: `GET /` agenda + month, `GET /api/classes` stub JSON,
`GET /partials/cards?query=&studio=&day=` card HTML,
`GET /partials/detail/{id}` detail modal HTML.
