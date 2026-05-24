"""
database.py — SQLite persistence layer
Tables: users, sessions, bookmarks, feedback, career_views
"""
from __future__ import annotations
import sqlite3, hashlib, os, json
from datetime import datetime
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "career_guidance.db")

# ── Schema ────────────────────────────────────────────────────────────────────
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL,
    email         TEXT    UNIQUE NOT NULL,
    password_hash TEXT    NOT NULL,
    created_at    TEXT    DEFAULT (datetime('now')),
    last_login    TEXT
);

CREATE TABLE IF NOT EXISTS sessions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email    TEXT    NOT NULL,
    stream        TEXT,
    field         TEXT,
    role          TEXT,
    hobby         TEXT,
    subject       TEXT,
    aspiration    TEXT,
    top_career    TEXT,
    all_results   TEXT,
    created_at    TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS bookmarks (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email    TEXT    NOT NULL,
    career        TEXT    NOT NULL,
    notes         TEXT,
    created_at    TEXT    DEFAULT (datetime('now')),
    UNIQUE(user_email, career)
);

CREATE TABLE IF NOT EXISTS feedback (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email    TEXT    NOT NULL,
    rating        INTEGER NOT NULL,
    comment       TEXT,
    feature       TEXT,
    created_at    TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS career_views (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    career        TEXT    NOT NULL,
    user_email    TEXT,
    viewed_at     TEXT    DEFAULT (datetime('now'))
);
"""

@contextmanager
def _conn():
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()

def init_db():
    with _conn() as con:
        con.executescript(SCHEMA)

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ── Users ─────────────────────────────────────────────────────────────────────
def register_user(name: str, email: str, password: str) -> tuple[bool, str]:
    try:
        with _conn() as con:
            con.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, _hash(password))
            )
        return True, "registered"
    except sqlite3.IntegrityError:
        return False, "email_exists"

def verify_login(email: str, password: str) -> tuple[bool, str]:
    with _conn() as con:
        row = con.execute(
            "SELECT name, password_hash FROM users WHERE email = ?", (email,)
        ).fetchone()
    if not row:
        return False, ""
    if row["password_hash"] == _hash(password):
        with _conn() as con:
            con.execute("UPDATE users SET last_login = datetime('now') WHERE email = ?", (email,))
        return True, row["name"]
    return False, ""

def get_user_count() -> int:
    with _conn() as con:
        return con.execute("SELECT COUNT(*) FROM users").fetchone()[0]

def get_all_users() -> list[dict]:
    with _conn() as con:
        rows = con.execute(
            "SELECT name, email, created_at, last_login FROM users ORDER BY created_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]

# ── Sessions ──────────────────────────────────────────────────────────────────
def save_session(user_email: str, inputs: dict, results: list):
    top = results[0][0] if results else ""
    all_r = json.dumps([{"career": c, "score": round(s, 4)} for c, s in results])
    with _conn() as con:
        con.execute("""
            INSERT INTO sessions (user_email, stream, field, role, hobby, subject,
                                  aspiration, top_career, all_results)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_email,
            inputs.get("stream", ""),
            inputs.get("field", ""),
            inputs.get("role", ""),
            inputs.get("hobby", ""),
            inputs.get("subject", ""),
            inputs.get("aspiration", ""),
            top, all_r,
        ))

def get_user_sessions(user_email: str) -> list[dict]:
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM sessions WHERE user_email = ? ORDER BY created_at DESC LIMIT 10",
            (user_email,)
        ).fetchall()
    return [dict(r) for r in rows]

def get_session_count() -> int:
    with _conn() as con:
        return con.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]

def get_top_careers_overall(limit: int = 10) -> list[tuple[str, int]]:
    with _conn() as con:
        rows = con.execute("""
            SELECT top_career, COUNT(*) as cnt
            FROM sessions WHERE top_career != ''
            GROUP BY top_career ORDER BY cnt DESC LIMIT ?
        """, (limit,)).fetchall()
    return [(r["top_career"], r["cnt"]) for r in rows]

def get_stream_distribution() -> dict[str, int]:
    with _conn() as con:
        rows = con.execute("""
            SELECT stream, COUNT(*) as cnt FROM sessions
            WHERE stream != '' GROUP BY stream
        """).fetchall()
    return {r["stream"]: r["cnt"] for r in rows}

# ── Bookmarks ─────────────────────────────────────────────────────────────────
def add_bookmark(user_email: str, career: str, notes: str = "") -> bool:
    try:
        with _conn() as con:
            con.execute(
                "INSERT INTO bookmarks (user_email, career, notes) VALUES (?, ?, ?)",
                (user_email, career, notes)
            )
        return True
    except sqlite3.IntegrityError:
        return False

def remove_bookmark(user_email: str, career: str):
    with _conn() as con:
        con.execute("DELETE FROM bookmarks WHERE user_email = ? AND career = ?", (user_email, career))

def get_bookmarks(user_email: str) -> list[dict]:
    with _conn() as con:
        rows = con.execute(
            "SELECT career, notes, created_at FROM bookmarks WHERE user_email = ? ORDER BY created_at DESC",
            (user_email,)
        ).fetchall()
    return [dict(r) for r in rows]

def is_bookmarked(user_email: str, career: str) -> bool:
    with _conn() as con:
        r = con.execute(
            "SELECT 1 FROM bookmarks WHERE user_email = ? AND career = ?", (user_email, career)
        ).fetchone()
    return r is not None

# ── Feedback ──────────────────────────────────────────────────────────────────
def save_feedback(user_email: str, rating: int, comment: str, feature: str = "general"):
    with _conn() as con:
        con.execute(
            "INSERT INTO feedback (user_email, rating, comment, feature) VALUES (?, ?, ?, ?)",
            (user_email, rating, comment, feature)
        )

def get_avg_rating() -> float:
    with _conn() as con:
        r = con.execute("SELECT AVG(rating) FROM feedback").fetchone()[0]
    return round(r or 0.0, 1)

def get_feedback_count() -> int:
    with _conn() as con:
        return con.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]

# ── Career views ──────────────────────────────────────────────────────────────
def log_career_view(career: str, user_email: str = ""):
    with _conn() as con:
        con.execute(
            "INSERT INTO career_views (career, user_email) VALUES (?, ?)", (career, user_email)
        )

def get_most_viewed(limit: int = 8) -> list[tuple[str, int]]:
    with _conn() as con:
        rows = con.execute("""
            SELECT career, COUNT(*) as cnt FROM career_views
            GROUP BY career ORDER BY cnt DESC LIMIT ?
        """, (limit,)).fetchall()
    return [(r["career"], r["cnt"]) for r in rows]

# Initialise on import
init_db()
