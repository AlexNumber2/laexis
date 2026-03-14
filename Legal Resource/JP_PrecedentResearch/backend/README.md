# JP Precedent Research (Phase 1 backend)

This backend implements the Phase 1 `/v1` APIs described in:

- `../phase1-search-field-mapping.md`
- `../phase1-cloudflare-deployment.md`

## What It Does

- Proxies precedent search against `courts.go.jp`
- Normalizes search results into JSON for the Laexis UI
- Fetches precedent detail pages
- Extracts PDF URL and page text preview
- Generates a heuristic summary (Phase 1). AI-provider integration is a Phase 1.5 task.

## Run (Local)

1. Create a venv and install requirements:

```powershell
cd "C:\Users\Alex\OneDrive\ドキュメント\Laexis Project\site\Legal Resource\JP_PrecedentResearch\backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Start the server:

```powershell
.\run.ps1
```

Backend will listen on `http://127.0.0.1:8000/v1`.

## CORS

Set `ALLOWED_ORIGINS` (comma-separated) for production:

```text
ALLOWED_ORIGINS=https://www.laexis.com,http://127.0.0.1:5500
```

## Notes

- Phase 1 uses a lightweight SQLite cache at `backend/data/cache.sqlite`.
- `tab=integrated` is the strongest Phase 1 path.
- Other tabs are routed to `search2` through `search7` with best-effort parsing.
