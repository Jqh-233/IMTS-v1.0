import sqlite3
from pathlib import Path


def connect(db_path: Path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path):
    with connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT,
                subject TEXT NOT NULL,
                sender TEXT NOT NULL,
                body TEXT NOT NULL,
                received_at TEXT NOT NULL,
                is_processed INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id INTEGER,
                task_name TEXT NOT NULL,
                deadline TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                category TEXT NOT NULL,
                confidence REAL NOT NULL,
                confidence_source TEXT NOT NULL DEFAULT 'rules',
                created_at TEXT NOT NULL,
                FOREIGN KEY(email_id) REFERENCES emails(id)
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_task_deadline ON tasks(deadline, status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_task_priority ON tasks(priority, status)")
        _ensure_column(conn, "tasks", "confidence_source", "TEXT NOT NULL DEFAULT 'rules'")


def _ensure_column(conn, table_name, column_name, definition):
    columns = {row["name"] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()}
    if column_name not in columns:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")
