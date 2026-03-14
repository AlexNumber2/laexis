# Phase 1 Search Field Mapping

## Goal

Phase 1 search UI should preserve the `Laexis` visual language while matching the structure of the Japanese court precedent search form as closely as possible for integrated search.

This document defines:

- the Phase 1 tabs
- the frontend form groups
- the backend query schema
- the mapping to the court site request parameters
- the implementation priority for each field

## Phase 1 Scope

Phase 1 supports:

- realtime proxy search against `https://www.courts.go.jp/hanrei/search1/index.html`
- integrated search as the primary live flow
- result list normalization
- detail fetch
- AI summary after selecting a precedent

Phase 1 does not yet require:

- full local precedent database
- Elasticsearch
- full parity for every specialized tab result parser

## Court Tabs To Mirror In UI

The search page should expose the same high-level tab model as the court site:

| UI tab | Court page target | Phase 1 status |
| --- | --- | --- |
| Integrated Search | `search1/index.html` | Full support |
| Supreme Court | `search2/index.html` | UI scaffold only |
| High Courts | `search3/index.html` | UI scaffold only |
| Lower Courts (速報) | `search4/index.html` | UI scaffold only |
| Administrative Cases | `search5/index.html` | UI scaffold only |
| Labor Cases | `search6/index.html` | UI scaffold only |
| Intellectual Property Cases | `search7/index.html` | UI scaffold only |

Phase 1 should fully wire only `Integrated Search`. The other tabs should exist in the UI and route through a common tab state so we do not redesign the page later.

## Frontend Form Model

Recommended frontend state object:

```ts
type SearchTab =
  | "integrated"
  | "supreme"
  | "high"
  | "lower"
  | "administrative"
  | "labor"
  | "ip";

type SearchFormState = {
  tab: SearchTab;
  query1: string;
  query2: string;
  judgeDateMode: "1" | "2" | "";
  judgeGengoFrom: string;
  judgeYearFrom: string;
  judgeMonthFrom: string;
  judgeDayFrom: string;
  judgeGengoTo: string;
  judgeYearTo: string;
  judgeMonthTo: string;
  judgeDayTo: string;
  jikenGengo: string;
  jikenYear: string;
  jikenCode: string;
  jikenNumber: string;
  courtType: string;
  courtSection: string;
  courtName: string;
  branchName: string;
  sort: "1" | "2" | "3";
  offset: string;
};
```

## Form Groups

### 1. Full Text Search

| UI label | Frontend key | Court param | Phase 1 |
| --- | --- | --- | --- |
| Main keyword | `query1` | `query1` | Required |
| Additional include keyword | `query2` | `query2` | Optional |

Behavior:

- `query1` is the primary keyword box.
- `query2` is hidden behind an expand action, matching the court site pattern.
- If both are empty, block submit.

## 2. Judgment Date

| UI label | Frontend key | Court param | Phase 1 |
| --- | --- | --- | --- |
| Date mode | `judgeDateMode` | `filter[judgeDateMode]` | Required if any date field used |
| Era from | `judgeGengoFrom` | `filter[judgeGengoFrom]` | Optional |
| Year from | `judgeYearFrom` | `filter[judgeYearFrom]` | Optional |
| Month from | `judgeMonthFrom` | `filter[judgeMonthFrom]` | Optional |
| Day from | `judgeDayFrom` | `filter[judgeDayFrom]` | Optional |
| Era to | `judgeGengoTo` | `filter[judgeGengoTo]` | Optional |
| Year to | `judgeYearTo` | `filter[judgeYearTo]` | Optional |
| Month to | `judgeMonthTo` | `filter[judgeMonthTo]` | Optional |
| Day to | `judgeDayTo` | `filter[judgeDayTo]` | Optional |

Recommended UI:

- radio switch for `single date` vs `date range`
- two rows of era/year/month/day controls
- helper note under the date block

Validation rules:

- if any `from` or `to` field is filled, send `judgeDateMode`
- if `judgeDateMode = 1`, we still keep the two-row structure in Phase 1 for implementation simplicity, but the UI should visually indicate single-date behavior
- do not try to convert Gregorian dates to Japanese era in Phase 1 automatically

## 3. Case Number

| UI label | Frontend key | Court param | Phase 1 |
| --- | --- | --- | --- |
| Era | `jikenGengo` | `filter[jikenGengo]` | Optional |
| Year | `jikenYear` | `filter[jikenYear]` | Optional |
| Symbol | `jikenCode` | `filter[jikenCode]` | Optional |
| Number | `jikenNumber` | `filter[jikenNumber]` | Optional |

Recommended UI:

- one compact row
- each field independent
- keep labels visible at all times

## 4. Court Name

| UI label | Frontend key | Court param | Phase 1 |
| --- | --- | --- | --- |
| Court type / trial level | `courtType` | `filter[courtType]` | Optional |
| Division / section | `courtSection` | `filter[courtSection]` | Optional |
| Court | `courtName` | `filter[courtName]` | Optional |
| Branch | `branchName` | `filter[branchName]` | Optional |

Recommended UI:

- one row on desktop
- two rows on narrower screens
- all fields rendered as select controls in the final implementation

Phase 1 simplification:

- if the full remote option lists are not yet loaded dynamically, we can ship static option sets for the first pass
- the backend should still preserve the exact target parameter names

## 5. Sort And Paging

| UI label | Frontend key | Court param | Phase 1 |
| --- | --- | --- | --- |
| Sort | `sort` | `sort` | Required |
| Result offset | `offset` | `offset` | Required |

Default values:

- `sort = 1`
- `offset = 0`

## Backend Request Schema

Recommended internal backend schema:

```json
{
  "tab": "integrated",
  "query1": "",
  "query2": "",
  "judgeDateMode": "",
  "judgeGengoFrom": "",
  "judgeYearFrom": "",
  "judgeMonthFrom": "",
  "judgeDayFrom": "",
  "judgeGengoTo": "",
  "judgeYearTo": "",
  "judgeMonthTo": "",
  "judgeDayTo": "",
  "jikenGengo": "",
  "jikenYear": "",
  "jikenCode": "",
  "jikenNumber": "",
  "courtType": "",
  "courtSection": "",
  "courtName": "",
  "branchName": "",
  "sort": "1",
  "offset": "0"
}
```

## Backend Mapping Rules

Recommended backend mapper output:

```python
mapped = {
    "query1": form.query1,
    "query2": form.query2,
    "filter[judgeDateMode]": form.judgeDateMode,
    "filter[judgeGengoFrom]": form.judgeGengoFrom,
    "filter[judgeYearFrom]": form.judgeYearFrom,
    "filter[judgeMonthFrom]": form.judgeMonthFrom,
    "filter[judgeDayFrom]": form.judgeDayFrom,
    "filter[judgeGengoTo]": form.judgeGengoTo,
    "filter[judgeYearTo]": form.judgeYearTo,
    "filter[judgeMonthTo]": form.judgeMonthTo,
    "filter[judgeDayTo]": form.judgeDayTo,
    "filter[jikenGengo]": form.jikenGengo,
    "filter[jikenYear]": form.jikenYear,
    "filter[jikenCode]": form.jikenCode,
    "filter[jikenNumber]": form.jikenNumber,
    "filter[courtType]": form.courtType,
    "filter[courtSection]": form.courtSection,
    "filter[courtName]": form.courtName,
    "filter[branchName]": form.branchName,
    "sort": form.sort or "1",
    "offset": form.offset or "0",
}
```

Rules:

- drop empty values before building the query string
- preserve exact parameter names expected by the court site
- do not rename fields inside the HTTP proxy layer
- keep one mapper per tab if tab-specific pages diverge later

## API Contract Recommendation

### Search Endpoint

`GET /api/search/cases`

Accepted query keys should match the frontend state as closely as possible:

- `tab`
- `query1`
- `query2`
- `judgeDateMode`
- `judgeGengoFrom`
- `judgeYearFrom`
- `judgeMonthFrom`
- `judgeDayFrom`
- `judgeGengoTo`
- `judgeYearTo`
- `judgeMonthTo`
- `judgeDayTo`
- `jikenGengo`
- `jikenYear`
- `jikenCode`
- `jikenNumber`
- `courtType`
- `courtSection`
- `courtName`
- `branchName`
- `sort`
- `offset`

### Search Response

```json
{
  "tab": "integrated",
  "count_text": "140件中 1～10件を表示",
  "results": [
    {
      "section": "最高裁判例",
      "title": "令和6(行ヒ)362 保有個人情報不開示決定処分取消請求事件",
      "detail_url": "https://www.courts.go.jp/hanrei/95570/detail2/index.html",
      "pdf_url": "https://www.courts.go.jp/assets/hanrei/hanrei-pdf-95570.pdf",
      "meta": [
        "令和8年2月20日",
        "最高裁判所第三小法廷"
      ],
      "tags": [
        "判決",
        "行政訴訟"
      ]
    }
  ]
}
```

## UI Implementation Priority

### Must Ship In Phase 1

- integrated search tab
- `query1`
- `query2`
- judgment date group
- case number group
- court name group
- sort
- offset-based paging

### Can Be Stubbed In Phase 1

- dynamic option loading for every tab-specific court list
- tab-specific parser variations outside integrated search
- advanced helper links such as code list popups

## Development Checklist

- redesign the current simple search card into a grouped search module
- add tabs above the form
- add an expand/collapse pattern for `query2`
- implement date mode radio state
- add the case number four-field row
- add the court four-field row
- refactor frontend search submit to send the full parameter set
- refactor backend search endpoint to map and forward the full parameter set
- log the normalized request payload for debugging

## Key Decision

Phase 1 should aim for **field parity first, parser parity second**.

That means:

- the search form structure should match the court site now
- integrated search should work end to end now
- specialized tabs can share the same frontend shell before their backends are fully completed
