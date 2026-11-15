"""SQLite swarm board (BoardPort)."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from control_eval.domain.messages import BoardMessage


class SqliteBoard:
    def __init__(self, db_path: Path) -> None:
        self._path = Path(db_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    body TEXT NOT NULL,
                    ts TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def reset(self, run_id: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM messages WHERE run_id = ?", (run_id,))
            conn.commit()

    def post(self, agent_id: str, text: str, *, run_id: str = "") -> BoardMessage:
        msg = BoardMessage.create(agent_id, text, run_id=run_id)
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO messages (run_id, agent_id, body, ts) VALUES (?, ?, ?, ?)",
                (msg.run_id, msg.agent_id, msg.body, msg.ts),
            )
            conn.commit()
        return msg

    def read(self, limit: int = 50, *, run_id: str = "") -> list[BoardMessage]:
        q = "SELECT run_id, agent_id, body, ts FROM messages"
        params: list[Any] = []
        if run_id:
            q += " WHERE run_id = ?"
            params.append(run_id)
        q += " ORDER BY id DESC LIMIT ?"
        params.append(max(1, min(int(limit), 200)))
        with self._connect() as conn:
            rows = conn.execute(q, params).fetchall()
        out = [
            BoardMessage(
                agent_id=r["agent_id"],
                body=r["body"],
                ts=r["ts"],
                run_id=r["run_id"],
            )
            for r in rows
        ]
        out.reverse()
        return out

    def stats(self, run_id: str) -> dict[str, Any]:
        with self._connect() as conn:
            n = conn.execute(
                "SELECT COUNT(*) AS c FROM messages WHERE run_id = ?", (run_id,)
            ).fetchone()["c"]
            agents = [
                r["agent_id"]
                for r in conn.execute(
                    "SELECT DISTINCT agent_id FROM messages WHERE run_id = ?",
                    (run_id,),
                ).fetchall()
            ]
        return {
            "run_id": run_id,
            "message_count": n,
            "agents": agents,
            "db_path": str(self._path),
        }
