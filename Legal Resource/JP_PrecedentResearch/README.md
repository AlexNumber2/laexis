# JP Precedent Research (Phase 1)

This folder contains the Phase 1 implementation described by:

- `phase1-search-field-mapping.md`
- `phase1-cloudflare-deployment.md`

## Frontend

- `index.html` is a Laexis-styled UI that mirrors the court site search form groups and tab model.
- `precedent.js` submits the form state to the Phase 1 backend and renders list, detail, and summary.

The frontend probes API base automatically:

- on `*.laexis.com` it tries same-origin `/v1`, then `https://api.laexis.com/v1`
- otherwise it tries `http://127.0.0.1:8000/v1`, `http://localhost:8000/v1`, then the hosted URLs

You can override the API base by setting `window.__API_BASE__` before loading `precedent.js`.

## Backend

See `backend/README.md`.

## Phase 1 Notes

- All court tabs are clickable in the UI.
- `Integrated Search` is the most complete Phase 1 flow.
- Other tabs are routed to their matching court search pages with best-effort parsing.
- Summary is heuristic in Phase 1. Provider-backed GenAI output is the next step once keys and model choices are finalized.
