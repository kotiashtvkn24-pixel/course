import sqlite3
from abc import ABC, abstractmethod
from dataclasses import replace
from datetime import datetime

from app.models import Greeting

_SCHEMA = """
CREATE TABLE IF NOT EXISTS greetings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient TEXT NOT NULL,
    send_at TEXT NOT NULL,
    style TEXT NOT NULL,
    text TEXT,
    repeat INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending',
    error TEXT
);
"""


def connect(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    return conn


def _iso(moment: datetime) -> str:
    return moment.isoformat(timespec="seconds")


class GreetingRepository(ABC):
    @abstractmethod
    def add(self, greeting: Greeting) -> Greeting: ...

    @abstractmethod
    def list_all(self) -> list[Greeting]: ...

    @abstractmethod
    def due(self, now: datetime) -> list[Greeting]: ...

    @abstractmethod
    def update(self, greeting: Greeting) -> None: ...

    @abstractmethod
    def delete(self, greeting_id: int) -> bool: ...


class SqliteGreetingRepository(GreetingRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def _fetch(self, sql: str, params: tuple = ()) -> list[Greeting]:
        return [
            Greeting(
                id=row["id"],
                recipient=row["recipient"],
                send_at=datetime.fromisoformat(row["send_at"]),
                style=row["style"],
                text=row["text"],
                repeat=bool(row["repeat"]),
                status=row["status"],
                error=row["error"],
            )
            for row in self._conn.execute(sql, params)
        ]

    def add(self, greeting: Greeting) -> Greeting:
        with self._conn:
            cursor = self._conn.execute(
                "INSERT INTO greetings (recipient, send_at, style, text, repeat) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    greeting.recipient,
                    _iso(greeting.send_at),
                    greeting.style,
                    greeting.text,
                    int(greeting.repeat),
                ),
            )
        return replace(greeting, id=cursor.lastrowid)

    def list_all(self) -> list[Greeting]:
        return self._fetch("SELECT * FROM greetings ORDER BY send_at")

    def due(self, now: datetime) -> list[Greeting]:
        return self._fetch(
            "SELECT * FROM greetings WHERE status = 'pending' AND send_at <= ? ORDER BY send_at",
            (_iso(now),),
        )

    def update(self, greeting: Greeting) -> None:
        with self._conn:
            self._conn.execute(
                "UPDATE greetings SET send_at = ?, status = ?, error = ? WHERE id = ?",
                (_iso(greeting.send_at), greeting.status, greeting.error, greeting.id),
            )

    def delete(self, greeting_id: int) -> bool:
        with self._conn:
            cursor = self._conn.execute("DELETE FROM greetings WHERE id = ?", (greeting_id,))
        return cursor.rowcount > 0
