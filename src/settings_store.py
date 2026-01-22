\
import sqlite3
from pathlib import Path
from typing import Any, Optional

DEFAULTS = {
    "weekly_target": 0,
    "workdays": 5,
    "daily_target_override": None,  # None => auto
    "selected_brands": None,        # None => all
    "logo_path": None,
    "critical_delay_days": 3,
}

def _connect(db_path: str):
    con = sqlite3.connect(db_path)
    con.execute(
        "CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)"
    )
    return con

def get_setting(db_path: str, key: str) -> Any:
    con = _connect(db_path)
    try:
        cur = con.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = cur.fetchone()
        if not row:
            return DEFAULTS.get(key)
        raw = row[0]
        # try parse json
        try:
            return __import__("json").loads(raw)
        except Exception:
            return raw
    finally:
        con.close()

def set_setting(db_path: str, key: str, value: Any) -> None:
    con = _connect(db_path)
    try:
        raw = __import__("json").dumps(value, ensure_ascii=False)
        con.execute(
            "INSERT INTO settings(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, raw),
        )
        con.commit()
    finally:
        con.close()

def get_all_settings(db_path: str) -> dict:
    s = {}
    for k in DEFAULTS.keys():
        s[k] = get_setting(db_path, k)
    return s
