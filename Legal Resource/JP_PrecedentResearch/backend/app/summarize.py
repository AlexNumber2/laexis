from __future__ import annotations

import re
from typing import Any


def _pick_block(text: str, heading: str, max_len: int = 1800) -> str | None:
    # Very rough Phase 1 extraction: find a heading and take following content.
    pattern = rf"{re.escape(heading)}\s*[\r\n]+(.+)"
    m = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return None
    block = m.group(1).strip()
    # Stop at next common heading if possible.
    stop = re.search(r"\n(主文|理由|事実|第\d+|別紙)\b", block)
    if stop:
        block = block[: stop.start()].strip()
    if len(block) > max_len:
        block = block[:max_len].rstrip() + " ..."
    return block or None


def heuristic_summary(raw_text: str) -> dict[str, Any]:
    text = (raw_text or "").strip()

    judgment_date = None
    m = re.search(r"(令和|平成|昭和|大正|明治)\d+年\d+月\d+日", text)
    if m:
        judgment_date = m.group(0)

    final_holding = _pick_block(text, "主文") or _pick_block(text, "判決") or None
    case_facts = (
        _pick_block(text, "事実")
        or _pick_block(text, "事案の概要")
        or _pick_block(text, "事実及び理由")
        or None
    )
    judge_reasoning = _pick_block(text, "理由") or _pick_block(text, "判断") or None

    # Fallback slices to avoid empty cards.
    if not case_facts and text:
        case_facts = (text[:1200].rstrip() + " ...") if len(text) > 1200 else text
    if not judge_reasoning and text:
        mid = text[len(text) // 3 : len(text) // 3 + 1400]
        judge_reasoning = (mid.rstrip() + " ...") if len(mid) > 1400 else mid

    return {
        "judgment_date": judgment_date or "",
        "case_facts": case_facts or "",
        "judge_reasoning": judge_reasoning or "",
        "final_holding": final_holding or "",
    }
