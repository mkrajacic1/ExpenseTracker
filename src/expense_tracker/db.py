import sqlite3
from pathlib import Path

from flask import current_app, g


SCHEMA_PATH = Path(__file__).parent / "schema.sql"

CATEGORIES = [
    "Salary",
    "Groceries",
    "Rent",
    "Transport",
    "Entertainment",
    "Utilities",
    "Health",
    "Other",
]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    conn = sqlite3.connect(current_app.config["DATABASE"])
    try:
        with conn:
            conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
            conn.executemany(
                "INSERT OR IGNORE INTO categories (name) VALUES (?)",
                [(category,) for category in CATEGORIES],
            )
    finally:
        conn.close()


def init_app(app):
    app.teardown_appcontext(close_db)