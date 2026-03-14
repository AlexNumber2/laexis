# Phase 1 Cloudflare Deployment Notes

## Goal

Deploy the Phase 1 precedent research product in a way that works cleanly with `www.laexis.com` already being managed through Cloudflare.

Phase 1 priorities:

- keep deployment simple
- keep HTTPS and routing clean
- avoid CORS pain where possible
- avoid accidental caching of dynamic search responses
- preserve a path to later scale-out

## Recommended Topology

### Recommended Production Layout

- frontend app: `https://www.laexis.com/jp-precedent-research`
- backend API: `https://api.laexis.com`

Why this is the best Phase 1 default:

- frontend and backend can deploy independently
- FastAPI can stay on its own runtime
- Cloudflare still fronts both origins
- it is easier to debug than a same-domain reverse proxy in the first pass

### Alternative Layout

- frontend app: `https://www.laexis.com/jp-precedent-research`
- backend API path: `https://www.laexis.com/api/precedents/...`

This reduces cross-origin concerns, but it usually requires an extra reverse proxy or Cloudflare Worker/edge routing layer. It is a good Phase 2 refinement, not the easiest Phase 1 starting point.

## Recommended Phase 1 Architecture

Browser flow:

1. user loads the UI from `www.laexis.com`
2. browser calls `api.laexis.com`
3. API proxy requests `courts.go.jp`
4. API normalizes results and returns JSON
5. user selects a precedent
6. API fetches detail and generates cached summary if needed

Core principle:

- the browser never talks to `courts.go.jp` directly
- all court scraping stays server-side

## Cloudflare Responsibilities

Cloudflare should handle:

- DNS
- TLS termination
- proxying
- basic WAF protection
- optional rate limiting
- static asset caching where safe

Cloudflare should not aggressively cache:

- search API responses
- detail API responses
- AI summary POST endpoints

## DNS Plan

Recommended records:

- `www.laexis.com` -> frontend origin, proxied through Cloudflare
- `api.laexis.com` -> backend origin, proxied through Cloudflare

Expected result:

- both frontend and backend are HTTPS through Cloudflare
- browser does not see origin IPs directly

## Routing Recommendation

### Frontend

Serve the precedent research page under one of these:

- `/jp-precedent-research`
- `/legal-resource/jp-precedent-research`

Recommendation:

- use `/legal-resource/jp-precedent-research` if you want to stay consistent with the current site information architecture
- use `/jp-precedent-research` if you want a shorter public URL

### API

Use versioned endpoints from the beginning:

- `https://api.laexis.com/v1/search/cases`
- `https://api.laexis.com/v1/cases/detail`
- `https://api.laexis.com/v1/cases/summarize`

Why:

- easier future expansion
- clearer API organization
- easier Cloudflare rules later

## CORS Recommendation

If frontend and backend are on separate subdomains:

- allow origin `https://www.laexis.com`
- allow methods `GET, POST, OPTIONS`
- allow headers `Content-Type, Authorization`
- do not use wildcard origins in production

Phase 1 recommendation:

- explicitly whitelist `https://www.laexis.com`
- whitelist local dev origins separately

Suggested dev list:

- `http://127.0.0.1:5500`
- `http://localhost:5500`
- `http://127.0.0.1:3000`
- `http://localhost:3000`

## Cache Strategy

### Safe To Cache

- CSS
- JS
- fonts
- static images

### Do Not Edge Cache

- `/v1/search/*`
- `/v1/cases/detail`
- `/v1/cases/summarize`

Why:

- search results vary heavily by query
- detail parsing can depend on fresh origin content
- summarize endpoints are user-triggered and stateful

### Application-Level Caching

Prefer caching inside the backend instead:

- search request snapshots
- detail HTML/text cache
- AI summary cache

This gives control without Cloudflare accidentally serving stale dynamic data.

## Security Recommendations

### Phase 1 Must-Haves

- enable Cloudflare proxy for `www` and `api`
- keep origin HTTPS enabled if possible
- only expose the backend through Cloudflare
- add basic rate limiting on the API
- log failed or abusive requests

### Phase 1 Nice-To-Haves

- Cloudflare WAF managed rules
- bot protection review
- challenge suspicious bursts of summarize requests

## Backend Hosting Recommendation

Phase 1 backend choices:

- VPS with FastAPI + reverse proxy
- container host
- managed Python app host

Requirement:

- backend must have reliable outbound access to `courts.go.jp`
- backend must support HTTPS behind Cloudflare

Practical recommendation:

- keep the backend on a simple Python-friendly host first
- let Cloudflare sit in front as the public edge

## Frontend Hosting Recommendation

Phase 1 frontend choices:

- existing site host if it already serves your `Laexis` pages
- static host fronted by Cloudflare

Requirement:

- frontend must be able to call the API using the production domain

## Environment Variables

Recommended frontend config:

- `API_BASE_URL=https://api.laexis.com/v1`

Recommended backend config:

- `ALLOWED_ORIGINS=https://www.laexis.com,http://127.0.0.1:5500,http://localhost:3000`
- `DATABASE_URL=...`
- `OPENAI_API_KEY=...` or equivalent
- `CACHE_ENABLED=true`

## Cloudflare Rule Checklist

### DNS

- proxy `www`
- proxy `api`

### SSL/TLS

- use Full or Full (strict) if origin supports it

### Cache Rules

- bypass cache for `/v1/search/*`
- bypass cache for `/v1/cases/*`
- cache static assets normally

### Security

- enable managed protections for the API zone/path
- add rate limiting to summarize endpoints

## Phase 1 Deployment Steps

1. deploy frontend to the intended production path
2. deploy FastAPI backend to its origin
3. create `api.laexis.com` DNS record in Cloudflare
4. enable proxy on the API DNS record
5. set backend CORS for `https://www.laexis.com`
6. add Cloudflare cache bypass rules for API paths
7. verify search, detail, and summarize requests over HTTPS

## Risks To Watch Early

### 1. Cross-Origin Misconfiguration

Symptom:

- frontend loads
- API calls fail in browser

Typical fix:

- correct CORS headers
- ensure API is called through the Cloudflare HTTPS hostname

### 2. Over-Caching Dynamic Endpoints

Symptom:

- repeated stale search results
- stale detail responses

Typical fix:

- bypass Cloudflare cache for API routes

### 3. Origin Exposure

Symptom:

- backend reachable outside Cloudflare

Typical fix:

- firewall to Cloudflare IPs only if infrastructure allows
- avoid publishing raw origin hostnames in frontend code

### 4. Scraping Reliability

Symptom:

- court requests fail or slow down

Typical fix:

- backend retries
- timeout control
- request logging

## Final Recommendation

For Phase 1, the cleanest deployment target is:

- `www.laexis.com` for the user-facing UI
- `api.laexis.com` for FastAPI
- Cloudflare proxy and TLS in front of both
- backend-level caching for dynamic court content
- no Cloudflare edge caching for the live API

This gives the shortest path to production while still staying compatible with a future move to richer API routing, Workers, or same-domain reverse proxying later.
