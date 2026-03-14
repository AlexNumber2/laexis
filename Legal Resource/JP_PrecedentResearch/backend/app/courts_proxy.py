from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import httpx

from .parsing import SEARCH1_URL


USER_AGENT = "Mozilla/5.0 (compatible; LaexisPrecedentResearch/1.0)"

TAB_CONFIG = {
    "integrated": {"path": "search1/index.html", "fixed": {}},
    "supreme": {"path": "search2/index.html", "fixed": {}},
    "high": {"path": "search3/index.html", "fixed": {}},
    "lower": {"path": "search4/index.html", "fixed": {}},
    "administrative": {"path": "search5/index.html", "fixed": {}},
    "labor": {"path": "search6/index.html", "fixed": {}},
    "ip": {"path": "search7/index.html", "fixed": {}},
}


@dataclass(frozen=True)
class CourtResponse:
    url: str
    text: str


async def fetch_text(url: str) -> CourtResponse:
    timeout = httpx.Timeout(30.0, connect=15.0)
    async with httpx.AsyncClient(
        headers={"User-Agent": USER_AGENT, "Accept-Language": "ja,en-US;q=0.8,en;q=0.6"},
        timeout=timeout,
        follow_redirects=True,
    ) as client:
        r = await client.get(url)
        r.raise_for_status()
        return CourtResponse(url=str(r.url), text=r.text)


def build_search_url(tab: str, mapped_params: dict[str, str]) -> str:
    cfg = TAB_CONFIG.get(tab) or TAB_CONFIG["integrated"]
    base = SEARCH1_URL.replace("search1/index.html", cfg["path"])
    params = {k: v for k, v in mapped_params.items() if v}
    params.update(cfg["fixed"])
    if "sort" not in params:
        params["sort"] = "1"
    if "offset" not in params:
        params["offset"] = "0"
    return f"{base}?{urlencode(params, doseq=True)}"


def map_phase1_query(query: dict[str, Any]) -> dict[str, str]:
    # Match the mapping doc: keep keys stable and map to court param names.
    mapped: dict[str, str] = {
        "query1": str(query.get("query1", "")).strip(),
        "query2": str(query.get("query2", "")).strip(),
        "filter[judgeDateMode]": str(query.get("judgeDateMode", "")).strip(),
        "filter[judgeGengoFrom]": str(query.get("judgeGengoFrom", "")).strip(),
        "filter[judgeYearFrom]": str(query.get("judgeYearFrom", "")).strip(),
        "filter[judgeMonthFrom]": str(query.get("judgeMonthFrom", "")).strip(),
        "filter[judgeDayFrom]": str(query.get("judgeDayFrom", "")).strip(),
        "filter[judgeGengoTo]": str(query.get("judgeGengoTo", "")).strip(),
        "filter[judgeYearTo]": str(query.get("judgeYearTo", "")).strip(),
        "filter[judgeMonthTo]": str(query.get("judgeMonthTo", "")).strip(),
        "filter[judgeDayTo]": str(query.get("judgeDayTo", "")).strip(),
        "filter[jikenGengo]": str(query.get("jikenGengo", "")).strip(),
        "filter[jikenYear]": str(query.get("jikenYear", "")).strip(),
        "filter[jikenCode]": str(query.get("jikenCode", "")).strip(),
        "filter[jikenNumber]": str(query.get("jikenNumber", "")).strip(),
        "filter[courtType]": str(query.get("courtType", "")).strip(),
        "filter[courtSection]": str(query.get("courtSection", "")).strip(),
        "filter[courtName]": str(query.get("courtName", "")).strip(),
        "filter[branchName]": str(query.get("branchName", "")).strip(),
        "sort": str(query.get("sort", "1")).strip() or "1",
        "offset": str(query.get("offset", "0")).strip() or "0",
    }
    return {k: v for k, v in mapped.items() if v}


async def fetch_with_retries(url: str) -> CourtResponse:
    last: Exception | None = None
    for _ in range(2):
        try:
            return await fetch_text(url)
        except Exception as e:  # noqa: BLE001
            last = e
            await asyncio.sleep(0.6)
    assert last is not None
    raise last
