from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup


SEARCH1_URL = "https://www.courts.go.jp/hanrei/search1/index.html"


@dataclass(frozen=True)
class SearchItem:
    section: str
    title: str
    detail_url: str
    pdf_url: str | None
    meta: list[str]
    tags: list[str]


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").replace("\xa0", " ")).strip()


def parse_count_text(html: str) -> str | None:
    m = re.search(r"<p>(\d+件中\s*\d+～\d+件を表示)</p>", html)
    return m.group(1) if m else None


def parse_search_results(html: str) -> list[SearchItem]:
    soup = BeautifulSoup(html, "lxml")
    searched = soup.find(id="searched") or soup
    items: list[SearchItem] = []

    for tr in searched.select("tr"):
        th = tr.find("th")
        td = tr.find("td")
        if not th or not td:
            continue

        detail_a = None
        for a in th.find_all("a"):
            href = a.get("href") or ""
            if re.search(r"\.\./\d+/detail\d+/index\.html$", href):
                detail_a = a
                break
        if not detail_a:
            continue

        section = _clean_text(detail_a.get_text(" ", strip=True))
        detail_url = urljoin(SEARCH1_URL, detail_a.get("href") or "")

        ps = [p.get_text(" ", strip=True) for p in td.find_all("p")]
        ps = [_clean_text(p) for p in ps if _clean_text(p)]
        title = ps[0] if ps else section

        meta = []
        tags: list[str] = []
        if len(ps) >= 2:
            meta.append(ps[1])
        if len(ps) >= 3:
            tags = [t for t in re.split(r"\s+", ps[2]) if t]

        pdf_url = None
        file_col = tr.find("td", class_=re.compile(r"file-col"))
        if file_col:
            a = file_col.find("a")
            if a and a.get("href"):
                href = a.get("href") or ""
                if "pdf" in href.lower():
                    pdf_url = urljoin(SEARCH1_URL, href)

        items.append(
            SearchItem(
                section=section,
                title=title,
                detail_url=detail_url,
                pdf_url=pdf_url,
                meta=meta,
                tags=tags,
            )
        )

    return items


def parse_detail_page(detail_url: str, html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")

    pdf_url = None
    meta = soup.find("meta", attrs={"name": "pdf_url"})
    if meta and meta.get("content"):
        pdf_url = meta["content"].strip() or None

    main = soup.find("main") or soup
    raw_text = _clean_text(main.get_text("\n", strip=True))

    preview_text = raw_text
    if len(preview_text) > 6000:
        preview_text = preview_text[:6000] + " ..."

    # Best-effort metadata extraction (Phase 1).
    judgment_date = None
    court_name = None
    case_number = None
    case_title = None

    # Try to find a line that looks like a date.
    date_m = re.search(r"(令和|平成|昭和|大正|明治)\d+年\d+月\d+日", raw_text)
    if date_m:
        judgment_date = date_m.group(0)

    # Try to parse common patterns in early lines.
    lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
    head = "\n".join(lines[:60])
    m = re.search(r"(令和|平成|昭和|大正|明治)\S*\(\S*\)\S+", head)
    if m:
        case_number = m.group(0)
    for candidate in lines[:60]:
        if candidate.endswith("裁判所") or "裁判所" in candidate:
            court_name = candidate
            break
    if lines:
        case_title = lines[0]

    return {
        "detail_url": detail_url,
        "pdf_url": pdf_url,
        "raw_text": raw_text,
        "preview_text": preview_text,
        "judgment_date": judgment_date,
        "court_name": court_name,
        "case_number": case_number,
        "case_title": case_title,
    }


def parse_court_data(html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")
    node = soup.find("script", attrs={"id": "court-data", "type": "application/json"})
    if not node or not node.string:
        return {"courts": []}
    try:
        data = json.loads(node.string)
    except Exception:
        return {"courts": []}
    return data
