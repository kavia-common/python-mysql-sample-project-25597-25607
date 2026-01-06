from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def tmp_sqlite_db(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """
    Create a temporary SQLite DB file with the expected schema for tests.
    """
    db_path = tmp_path_factory.mktemp("db") / "test_myapp.db"
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
    finally:
        conn.close()
    return db_path


@pytest.fixture()
def app_client(monkeypatch: pytest.MonkeyPatch, tmp_sqlite_db: Path):
    """
    Provide a Flask test client with DB path discovery patched to point at the temp DB.
    """
    # Import the app after patching the DB connection file location expectations by
    # overriding get_db_path() in app.db module.
    from app import db as app_db
    from app import app as flask_app

    monkeypatch.setattr(app_db, "get_db_path", lambda: os.path.abspath(str(tmp_sqlite_db)))

    flask_app.config.update(
        {
            "TESTING": True,
        }
    )

    with flask_app.test_client() as client:
        yield client
