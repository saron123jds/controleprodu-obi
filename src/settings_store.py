from __future__ import annotations

import json
import sqlite3
from pathlib import Path


def _init_db(db_path: str) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS upload_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                path TEXT,
                uploaded_at TEXT
            )
            """
        )
        conn.commit()


def set_setting(db_path: str, key: str, value) -> None:
    _init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, json.dumps(value)),
        )
        conn.commit()


def get_setting(db_path: str, key: str, default=None):
    _init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        if not row:
            return default
        return json.loads(row[0])


def get_all_settings(db_path: str) -> dict:
    _init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("SELECT key, value FROM settings")
        rows = cursor.fetchall()
        return {key: json.loads(value) for key, value in rows}


def add_upload_history(db_path: str, filename: str, path: str, uploaded_at: str) -> None:
    _init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO upload_history (filename, path, uploaded_at) VALUES (?, ?, ?)",
            (filename, path, uploaded_at),
        )
        conn.commit()


def get_upload_history(db_path: str, limit: int = 10) -> list[dict]:
    _init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            "SELECT filename, path, uploaded_at FROM upload_history ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        return [
            {"filename": filename, "path": path, "uploaded_at": uploaded_at}
            for filename, path, uploaded_at in rows
        ]
