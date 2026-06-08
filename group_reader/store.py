"""
SQLite message store — persists group messages across restarts.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "messages.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id     INTEGER NOT NULL,
                group_name   TEXT,
                message_id   INTEGER NOT NULL,
                sender       TEXT,
                text         TEXT,
                timestamp    TEXT NOT NULL,
                UNIQUE(group_id, message_id)
            )
        """)


def save_message(group_id: int, group_name: str, message_id: int,
                 sender: str, text: str, timestamp: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """INSERT OR IGNORE INTO messages
               (group_id, group_name, message_id, sender, text, timestamp)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (group_id, group_name, message_id, sender, text, timestamp)
        )


def get_recent(group_id: int, limit: int = 100) -> list[dict]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """SELECT sender, text, timestamp FROM messages
               WHERE group_id = ? AND text IS NOT NULL AND text != ''
               ORDER BY id DESC LIMIT ?""",
            (group_id, limit)
        ).fetchall()
    return [dict(r) for r in reversed(rows)]


def list_groups() -> list[dict]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """SELECT group_id, group_name, COUNT(*) as msg_count
               FROM messages GROUP BY group_id"""
        ).fetchall()
    return [dict(r) for r in rows]
