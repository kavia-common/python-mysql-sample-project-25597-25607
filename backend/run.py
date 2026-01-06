"""
Backend entrypoint.

Runs the Flask API server.

Environment variables:
- PORT: Port to bind to (defaults to 8000).
- HOST: Host to bind to (defaults to 0.0.0.0).
- FLASK_DEBUG: Set to "1" to enable debug mode.
"""

from __future__ import annotations

import os

from app import app


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug)
