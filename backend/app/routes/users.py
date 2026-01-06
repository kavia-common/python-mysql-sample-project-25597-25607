from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional

from flask.views import MethodView
from flask_smorest import Blueprint, abort

from ..db import get_connection
from ..schemas.users import UserCreateSchema, UserSchema, UserUpdateSchema

blp = Blueprint(
    "Users",
    "users",
    url_prefix="/api/users",
    description="CRUD operations for users.",
)


def _row_to_user_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert sqlite Row to JSON-serializable dict."""
    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "created_at": row["created_at"],
    }


def _fetch_user_by_id(conn: sqlite3.Connection, user_id: int) -> Optional[Dict[str, Any]]:
    cur = conn.execute(
        "SELECT id, name, email, created_at FROM users WHERE id = ?",
        (user_id,),
    )
    row = cur.fetchone()
    return _row_to_user_dict(row) if row else None


@blp.route("/")
class UsersCollection(MethodView):
    @blp.response(200, UserSchema(many=True))
    def get(self):
        """List users."""
        conn = get_connection()
        try:
            cur = conn.execute("SELECT id, name, email, created_at FROM users ORDER BY id ASC")
            rows = cur.fetchall()
            return [_row_to_user_dict(r) for r in rows]
        finally:
            conn.close()

    @blp.arguments(UserCreateSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data: Dict[str, Any]):
        """Create a user."""
        conn = get_connection()
        try:
            try:
                cur = conn.execute(
                    "INSERT INTO users (name, email) VALUES (?, ?)",
                    (user_data["name"], user_data["email"]),
                )
                conn.commit()
            except sqlite3.IntegrityError:
                # Unique constraint on email
                abort(409, message="User with this email already exists.")
            user_id = int(cur.lastrowid)
            user = _fetch_user_by_id(conn, user_id)
            if not user:
                abort(500, message="Failed to load created user.")
            return user
        finally:
            conn.close()


@blp.route("/<int:user_id>")
class UsersItem(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id: int):
        """Get user by id."""
        conn = get_connection()
        try:
            user = _fetch_user_by_id(conn, user_id)
            if not user:
                abort(404, message="User not found.")
            return user
        finally:
            conn.close()

    @blp.arguments(UserUpdateSchema)
    @blp.response(200, UserSchema)
    def patch(self, user_data: Dict[str, Any], user_id: int):
        """Update a user (partial update)."""
        if not user_data:
            abort(400, message="No fields provided for update.")

        conn = get_connection()
        try:
            existing = _fetch_user_by_id(conn, user_id)
            if not existing:
                abort(404, message="User not found.")

            fields: List[str] = []
            values: List[Any] = []

            if "name" in user_data:
                fields.append("name = ?")
                values.append(user_data["name"])
            if "email" in user_data:
                fields.append("email = ?")
                values.append(user_data["email"])

            if not fields:
                abort(400, message="No valid fields provided for update.")

            values.append(user_id)

            try:
                conn.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = ?", tuple(values))
                conn.commit()
            except sqlite3.IntegrityError:
                abort(409, message="User with this email already exists.")

            updated = _fetch_user_by_id(conn, user_id)
            if not updated:
                abort(500, message="Failed to load updated user.")
            return updated
        finally:
            conn.close()

    @blp.arguments(UserUpdateSchema)
    @blp.response(200, UserSchema)
    def put(self, user_data: Dict[str, Any], user_id: int):
        """Update a user (full update)."""
        # Treat PUT as requiring both fields for this simple API.
        if "name" not in user_data or "email" not in user_data:
            abort(400, message="PUT requires both 'name' and 'email'.")

        conn = get_connection()
        try:
            existing = _fetch_user_by_id(conn, user_id)
            if not existing:
                abort(404, message="User not found.")

            try:
                conn.execute(
                    "UPDATE users SET name = ?, email = ? WHERE id = ?",
                    (user_data["name"], user_data["email"], user_id),
                )
                conn.commit()
            except sqlite3.IntegrityError:
                abort(409, message="User with this email already exists.")

            updated = _fetch_user_by_id(conn, user_id)
            if not updated:
                abort(500, message="Failed to load updated user.")
            return updated
        finally:
            conn.close()

    @blp.response(204)
    def delete(self, user_id: int):
        """Delete a user."""
        conn = get_connection()
        try:
            cur = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            if cur.rowcount == 0:
                abort(404, message="User not found.")
            return ""
        finally:
            conn.close()
