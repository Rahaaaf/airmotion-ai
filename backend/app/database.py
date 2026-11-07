import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
DB_PATH = BASE / "backend" / "app" / "airmotion.db"

DEFAULT_MAPPINGS = {
    "UP": "SCROLL_UP",
    "DOWN": "SCROLL_DOWN",
    "LEFT": "GO_BACK",
    "RIGHT": "GO_FORWARD",
    "CIRCLE": "NEW_TAB",
    "SHAKE": "RELOAD_PAGE",
    "UNKNOWN": "NONE",
}


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mappings (
                gesture_id TEXT PRIMARY KEY,
                action_id TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                gesture_id TEXT NOT NULL,
                action_id TEXT NOT NULL,
                confidence REAL NOT NULL,
                detected_at TEXT NOT NULL,
                device_id TEXT NOT NULL,
                sequence_number INTEGER NOT NULL
            )
            """
        )

        existing = conn.execute("SELECT gesture_id, action_id FROM mappings").fetchall()
        if not existing:
            conn.executemany(
                "INSERT INTO mappings (gesture_id, action_id) VALUES (?, ?)",
                list(DEFAULT_MAPPINGS.items()),
            )


def get_mappings():
    with get_connection() as conn:
        rows = conn.execute("SELECT gesture_id, action_id FROM mappings").fetchall()

    mappings = {row["gesture_id"]: row["action_id"] for row in rows}
    for gesture, action in DEFAULT_MAPPINGS.items():
        mappings.setdefault(gesture, action)
    return mappings


def update_mappings(mappings):
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO mappings (gesture_id, action_id)
            VALUES (?, ?)
            ON CONFLICT(gesture_id)
            DO UPDATE SET action_id=excluded.action_id
            """,
            list(mappings.items()),
        )
    return get_mappings()


def save_event(event):
    mappings = get_mappings()
    action = mappings.get(event["gesture_id"], "NONE")
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO events (
                event_id,
                gesture_id,
                action_id,
                confidence,
                detected_at,
                device_id,
                sequence_number
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event["event_id"],
                event["gesture_id"],
                action,
                float(event["confidence"]),
                event["detected_at"],
                event["device_id"],
                event["sequence_number"],
            ),
        )
    return {**event, "action_id": action}


def get_events(limit=100):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM events
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]
