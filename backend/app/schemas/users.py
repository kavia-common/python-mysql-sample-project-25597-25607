"""Marshmallow schemas for users API."""
from __future__ import annotations

from marshmallow import Schema, fields


class UserSchema(Schema):
    """A persisted user record."""
    id = fields.Int(required=True, dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    created_at = fields.Str(required=False, dump_only=True)


class UserCreateSchema(Schema):
    """Payload for creating a user."""
    name = fields.Str(required=True)
    email = fields.Email(required=True)


class UserUpdateSchema(Schema):
    """Payload for updating a user. All fields optional for PATCH semantics."""
    name = fields.Str(required=False)
    email = fields.Email(required=False)
