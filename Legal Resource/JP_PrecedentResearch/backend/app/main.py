from __future__ import annotations

import os
import time
from typing import Any, Optional

from fastapi import Body, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .courts_proxy import build_search_url, fetch_with_retries, map_phase1_query
from .parsing import parse_court_data, parse_count_text, parse_detail_page, parse_search_results
from .storage import CachedCase, Storage
from .summarize import heuristic_summary


HERE = os.path.dirname(__file__)
DB_PATH = os.path.join(HERE, "..", "data", "cache.sqlite")
storage = Storage(os.path.abspath(DB_PATH))


def _no_store(payload: dict[str, Any]) -> JSONResponse:
    resp = JSONResponse(payload)
    resp.headers["Cache-Control"] = "no-store"
    return resp


def _origins() -> list[str]:
    raw = os.environ.get("ALLOWED_ORIGINS", "").strip()
    if raw:
        return [o.strip() for o in raw.split(",") if o.strip()]
    return [
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ]


app = FastAPI(title="Laexis JP Precedent Research API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


_meta_cache: dict[str, Any] = {"loaded_at": 0.0, "payload": None}


@app.get("/v1/health")
def health() -> JSONResponse:
    return _no_store({"ok": True, "ts": time.time()})


@app.get("/v1/meta/courts")
async def meta_courts() -> JSONResponse:
    # Phase 1 helper endpoint to populate selects/datalists in the UI.
    # Cache in memory for one day.
    if _meta_cache["payload"] and time.time() - float(_meta_cache["loaded_at"]) < 86400:
        return _no_store(_meta_cache["payload"])

    try:
        res = await fetch_with_retries("https://www.courts.go.jp/hanrei/search1/index.html")
        data = parse_court_data(res.text)
        courts = data.get("courts", []) or []

        # Derive courtTypes and sections from the court list.
        type_map: dict[str, str] = {}
        section_map: dict[str, str] = {}
        branches: list[dict[str, str]] = []
        for c in courts:
            t = str(c.get("type", "")).strip()
            tn = str(c.get("typeName", "")).strip()
            if t and tn:
                type_map[t] = tn
            s = str(c.get("section", "")).strip()
            if s:
                # The integrated search uses numeric sections. Names differ by page logic.
                # Phase 1 keeps these as ids; UI can show fallback labels.
                section_map.setdefault(s, f"Section {s}")

        payload = {
            "courtTypes": [{"id": k, "name": v} for k, v in sorted(type_map.items(), key=lambda x: x[0])],
            "courtSections": [{"id": k, "name": v} for k, v in sorted(section_map.items(), key=lambda x: x[0])],
            "courts": [{"name": c.get("name"), "prefectureName": c.get("prefectureName")} for c in courts],
            "branches": branches,
        }
        _meta_cache["loaded_at"] = time.time()
        _meta_cache["payload"] = payload
        return _no_store(payload)
    except Exception as e:  # noqa: BLE001
        storage.log_error("meta_courts", str(e), "https://www.courts.go.jp/hanrei/search1/index.html")
        return _no_store({"courtTypes": [], "courtSections": [], "courts": [], "branches": []})


@app.get("/v1/search/cases")
async def search_cases(
    tab: str = Query(default="integrated"),
    query1: str = Query(default=""),
    query2: str = Query(default=""),
    judgeDateMode: str = Query(default=""),
    judgeGengoFrom: str = Query(default=""),
    judgeYearFrom: str = Query(default=""),
    judgeMonthFrom: str = Query(default=""),
    judgeDayFrom: str = Query(default=""),
    judgeGengoTo: str = Query(default=""),
    judgeYearTo: str = Query(default=""),
    judgeMonthTo: str = Query(default=""),
    judgeDayTo: str = Query(default=""),
    jikenGengo: str = Query(default=""),
    jikenYear: str = Query(default=""),
    jikenCode: str = Query(default=""),
    jikenNumber: str = Query(default=""),
    courtType: str = Query(default=""),
    courtSection: str = Query(default=""),
    courtName: str = Query(default=""),
    branchName: str = Query(default=""),
    sort: str = Query(default="1"),
    offset: str = Query(default="0"),
) -> JSONResponse:
    q = {
        "tab": tab,
        "query1": query1,
        "query2": query2,
        "judgeDateMode": judgeDateMode,
        "judgeGengoFrom": judgeGengoFrom,
        "judgeYearFrom": judgeYearFrom,
        "judgeMonthFrom": judgeMonthFrom,
        "judgeDayFrom": judgeDayFrom,
        "judgeGengoTo": judgeGengoTo,
        "judgeYearTo": judgeYearTo,
        "judgeMonthTo": judgeMonthTo,
        "judgeDayTo": judgeDayTo,
        "jikenGengo": jikenGengo,
        "jikenYear": jikenYear,
        "jikenCode": jikenCode,
        "jikenNumber": jikenNumber,
        "courtType": courtType,
        "courtSection": courtSection,
        "courtName": courtName,
        "branchName": branchName,
        "sort": sort,
        "offset": offset,
    }
    try:
        mapped = map_phase1_query(q)
        url = build_search_url(tab, mapped)
        res = await fetch_with_retries(url)
        count_text = parse_count_text(res.text)
        items = parse_search_results(res.text)
        results = [
            {
                "section": i.section,
                "title": i.title,
                "detail_url": i.detail_url,
                "pdf_url": i.pdf_url,
                "meta": i.meta,
                "tags": i.tags,
            }
            for i in items
        ]
        storage.log_search(q, len(results))
        return _no_store({"tab": tab, "count_text": count_text, "results": results})
    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001
        storage.log_error("search_cases", str(e))
        raise HTTPException(status_code=502, detail="Search proxy failed.") from e


@app.get("/v1/cases/detail")
async def case_detail(detail_url: str = Query(...)) -> JSONResponse:
    cached = storage.get_case(detail_url)
    if cached:
        return _no_store(
            {
                "detail_url": cached.detail_url,
                "case_title": cached.case_title,
                "case_number": cached.case_number,
                "court_name": cached.court_name,
                "judgment_date": cached.judgment_date,
                "pdf_url": cached.pdf_url,
                "raw_text": cached.raw_text,
                "preview_text": cached.preview_text,
            }
        )

    try:
        res = await fetch_with_retries(detail_url)
        parsed = parse_detail_page(detail_url, res.text)
        case = CachedCase(
            detail_url=detail_url,
            case_title=parsed.get("case_title"),
            case_number=parsed.get("case_number"),
            court_name=parsed.get("court_name"),
            judgment_date=parsed.get("judgment_date"),
            pdf_url=parsed.get("pdf_url"),
            raw_text=parsed.get("raw_text"),
            preview_text=parsed.get("preview_text"),
            fetched_at=time.time(),
        )
        storage.put_case(case)
        return _no_store(parsed)
    except Exception as e:  # noqa: BLE001
        storage.log_error("case_detail", str(e), detail_url)
        raise HTTPException(status_code=502, detail="Detail fetch failed.") from e


@app.post("/v1/cases/summarize")
async def summarize_case(payload: dict[str, Any] = Body(...)) -> JSONResponse:
    detail_url = str(payload.get("detail_url", "")).strip()
    mode = str(payload.get("mode", "summary_zh")).strip() or "summary_zh"
    if not detail_url:
        raise HTTPException(status_code=400, detail="detail_url is required.")

    cached = storage.get_summary(detail_url, mode)
    if cached:
        return _no_store(cached)

    try:
        case = storage.get_case(detail_url)
        if not case:
            # Fetch and cache detail first.
            res = await fetch_with_retries(detail_url)
            parsed = parse_detail_page(detail_url, res.text)
            case = CachedCase(
                detail_url=detail_url,
                case_title=parsed.get("case_title"),
                case_number=parsed.get("case_number"),
                court_name=parsed.get("court_name"),
                judgment_date=parsed.get("judgment_date"),
                pdf_url=parsed.get("pdf_url"),
                raw_text=parsed.get("raw_text"),
                preview_text=parsed.get("preview_text"),
                fetched_at=time.time(),
            )
            storage.put_case(case)

        summary = heuristic_summary(case.raw_text or "")
        storage.put_summary(detail_url, mode, summary)
        return _no_store(summary)
    except Exception as e:  # noqa: BLE001
        storage.log_error("summarize_case", str(e), detail_url)
        raise HTTPException(status_code=502, detail="Summarize failed.") from e
