from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "companion.db"
VALID_ROLES = {"user", "assistant", "system"}


@dataclass(frozen=True)
class StoredMessage:
    id: int
    role: str
    content: str
    created_at: str


class StorageService:
    """SQLite storage boundary for lightweight chat memory."""

    def __init__(self, settings: Any, db_path: Path = DATABASE_PATH) -> None:
        self.settings = settings
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.initialize()

    def initialize(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at)"
            )

    def add_message(self, role: str, content: str) -> int | None:
        if not self._memory_enabled:
            return None

        clean_role = role.strip().lower()
        clean_content = content.strip()
        if clean_role not in VALID_ROLES:
            raise ValueError(f"Unsupported message role: {role}")
        if not clean_content:
            return None

        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO messages (role, content, created_at) VALUES (?, ?, ?)",
                (clean_role, clean_content, created_at),
            )
            message_id = int(cursor.lastrowid)
        self.logger.info("Stored message: role=%s id=%s", clean_role, message_id)
        return message_id

    def get_recent_messages(self, limit: int = 20) -> list[StoredMessage]:
        if not self._memory_enabled:
            return []

        safe_limit = max(1, int(limit))
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, role, content, created_at
                FROM messages
                ORDER BY id DESC
                LIMIT ?
                """,
                (safe_limit,),
            ).fetchall()

        return list(reversed([self._row_to_message(row) for row in rows]))

    def count_messages(self) -> int:
        with self._connect() as connection:
            row = connection.execute("SELECT COUNT(*) FROM messages").fetchone()
        return int(row[0]) if row else 0

    def clear_messages(self) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM messages")
        self.logger.info("Stored chat memory cleared")

    def replace_chat_history(self, messages: Iterable[StoredMessage]) -> list[dict[str, str]]:
        return [{"role": message.role, "content": message.content} for message in messages]

    @property
    def _memory_enabled(self) -> bool:
        return bool(getattr(self.settings, "memory_enabled", True))

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _row_to_message(self, row: sqlite3.Row) -> StoredMessage:
        return StoredMessage(
            id=int(row["id"]),
            role=str(row["role"]),
            content=str(row["content"]),
            created_at=str(row["created_at"]),
        )
