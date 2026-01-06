"""
SQLite database utilities for the backend.

The SQLite database path is owned by the `database` container and must be read from:
  ../database/db_connection.txt (relative to backend container workspace)

This module centralizes DB-path discovery and connection creation so routes can
remain focused on request handling.
"""

from __future__ import annotations

import os
import re
import sqlite3
from typing import Optional


def _extract_db_path_from_db_connection_file(contents: str) -> Optional[str]:
    """
    Parse db_connection.txt contents and return the SQLite file path if found.

    Expected to find a line like:
      # File path: /abs/path/to/myapp.db
    Or alternatively a connection string like:
      # Connection string: sqlite:////abs/path/to/myapp.db
    """
    m = re.search(r"^\s*#\s*File path:\s*(.+?)\s*$", contents, flags=re.MULTILINE)
    if m:
        return m.group(1).strip()

    m = re.search(
        r"^\s*#\s*Connection string:\s*(sqlite:/{2,}.+?)\s*$",
        contents,
        flags=re.MULTILINE,
    )
    if m:
        uri = m.group(1).strip()
        # Common form used in this repo: sqlite:////abs/path/to/file.db
        if uri.startswith("sqlite:////"):
            return "/" + uri[len("sqlite:////") :].lstrip("/")
        if uri.startswith("sqlite:///"):
            return uri[len("sqlite:///") :]
        return uri

    return None


# PUBLIC_INTERFACE
def get_db_path() -> str:
    """Return absolute path to the SQLite database file as defined in database/db_connection.txt."""
    # backend/app/db.py -> backend/app -> backend -> workspace root
    backend_workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    db_connection_file = os.path.abspath(
        os.path.join(backend_workspace, "..", "database", "db_connection.txt")
    )

    if not os.path.exists(db_connection_file):
        raise FileNotFoundError(
            f"Required DB connection file not found at '{db_connection_file}'. "
            "The backend expects the database container to provide it."
        )

    with open(db_connection_file, "r", encoding="utf-8") as f:
        contents = f.read()

    db_path = _extract_db_path_from_db_connection_file(contents)
    if not db_path:
        raise ValueError(
            f"Could not determine SQLite DB path from '{db_connection_file}'. "
            "Expected a line like '# File path: /abs/path/to/myapp.db'."
        )

    return os.path.abspath(os.path.expanduser(db_path))


# PUBLIC_INTERFACE
def get_connection() -> sqlite3.Connection:
    """
    Create a new SQLite connection to the configured database.

    Notes:
    - Sets row_factory for dict-like access.
    - Enables foreign key enforcement.
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
