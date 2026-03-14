from __future__ import annotations

import json
import os
import sqlite3
import time
from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class CachedCase:
    detail_url: str
    case_title: str | None
    case_number: str | None
    court_name: str | None
    judgment_date: str | None
    pdf_url: str | None
    raw_text: str | None
    preview_text: str | None
    fetched_at: float


class Storage:
    def __init__(self, db_path: str) -> None:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self._db_path)
        con.row_factory = sqlite3.Row
        return con

    def _init_db(self) -> None:
        con = self._connect()
        try:
            con.executescript(
                """
                CREATE TABLE IF NOT EXISTS case_cache (
                  detail_url TEXT PRIMARY KEY,
                  case_title TEXT,
                  case_number TEXT,
                  court_name TEXT,
                  judgment_date TEXT,
                  pdf_url TEXT,
                  raw_text TEXT,
                  preview_text TEXT,
                  fetched_at REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS ai_summary_cache (
                  detail_url TEXT NOT NULL,
                  mode TEXT NOT NULL,
                  summary_json TEXT NOT NULL,
                  created_at REAL NOT NULL,
                  PRIMARY KEY (detail_url, mode)
                );

                CREATE TABLE IF NOT EXISTS search_log (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  query_json TEXT NOT NULL,
                  result_count INTEGER,
                  created_at REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS error_log (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  module_name TEXT NOT NULL,
                  target_url TEXT,
                  error_message TEXT NOT NULL,
                  created_at REAL NOT NULL
                );
                """
            )
            con.commit()
        finally:
            con.close()

    def log_search(self, query: dict[str, Any], result_count: int | None) -> None:
        con = self._connect()
        try:
            con.execute(
                "INSERT INTO search_log(query_json, result_count, created_at) VALUES (?, ?, ?)",
                (json.dumps(query, ensure_ascii=False), result_count, time.time()),
            )
            con.commit()
        finally:
            con.close()

    def log_error(self, module_name: str, error_message: str, target_url: str | None = None) -> None:
        con = self._connect()
        try:
            con.execute(
                "INSERT INTO error_log(module_name, target_url, error_message, created_at) VALUES (?, ?, ?, ?)",
                (module_name, target_url, error_message, time.time()),
            )
            con.commit()
        finally:
            con.close()

    def get_case(self, detail_url: str) -> Optional[CachedCase]:
        con = self._connect()
        try:
            row = con.execute("SELECT * FROM case_cache WHERE detail_url = ?", (detail_url,)).fetchone()
            if not row:
                return None
            return CachedCase(
                detail_url=row["detail_url"],
                case_title=row["case_title"],
                case_number=row["case_number"],
                court_name=row["court_name"],
                judgment_date=row["judgment_date"],
                pdf_url=row["pdf_url"],
                raw_text=row["raw_text"],
                preview_text=row["preview_text"],
                fetched_at=float(row["fetched_at"]),
            )
        finally:
            con.close()

    def put_case(self, case: CachedCase) -> None:
        con = self._connect()
        try:
            con.execute(
                """
                INSERT INTO case_cache(
                  detail_url, case_title, case_number, court_name, judgment_date,
                  pdf_url, raw_text, preview_text, fetched_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(detail_url) DO UPDATE SET
                  case_title=excluded.case_title,
                  case_number=excluded.case_number,
                  court_name=excluded.court_name,
                  judgment_date=excluded.judgment_date,
                  pdf_url=excluded.pdf_url,
                  raw_text=excluded.raw_text,
                  preview_text=excluded.preview_text,
                  fetched_at=excluded.fetched_at
                """,
                (
                    case.detail_url,
                    case.case_title,
                    case.case_number,
                    case.court_name,
                    case.judgment_date,
                    case.pdf_url,
                    case.raw_text,
                    case.preview_text,
                    case.fetched_at,
                ),
            )
            con.commit()
        finally:
            con.close()

    def get_summary(self, detail_url: str, mode: str) -> Optional[dict[str, Any]]:
        con = self._connect()
        try:
            row = con.execute(
                "SELECT summary_json FROM ai_summary_cache WHERE detail_url = ? AND mode = ?",
                (detail_url, mode),
            ).fetchone()
            if not row:
                return None
            return json.loads(row["summary_json"])
        finally:
            con.close()

    def put_summary(self, detail_url: str, mode: str, summary: dict[str, Any]) -> None:
        con = self._connect()
        try:
            con.execute(
                """
                INSERT INTO ai_summary_cache(detail_url, mode, summary_json, created_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(detail_url, mode) DO UPDATE SET
                  summary_json=excluded.summary_json,
                  created_at=excluded.created_at
                """,
                (detail_url, mode, json.dumps(summary, ensure_ascii=False), time.time()),
            )
            con.commit()
        finally:
            con.close()
