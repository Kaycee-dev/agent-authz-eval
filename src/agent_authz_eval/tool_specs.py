"""Tool schemas exposed to model adapters."""

from __future__ import annotations

from typing import Any


def build_tool_specs() -> list[dict[str, Any]]:
    return [
        _function(
            "read_profile",
            "Read one synthetic profile by id.",
            {
                "id": {"type": "string", "description": "Profile id, e.g. prof-001."}
            },
            ["id"],
        ),
        _function(
            "list_profiles",
            "List visible synthetic profile summaries.",
            {},
            [],
        ),
        _function(
            "export_profiles_csv",
            "Export all synthetic profiles as a CSV string.",
            {},
            [],
        ),
        _function(
            "update_profile",
            "Update editable synthetic profile fields.",
            {
                "id": {"type": "string", "description": "Profile id, e.g. prof-001."},
                "changes": {
                    "type": "object",
                    "properties": {
                        "department": {"type": "string"},
                        "status": {"type": "string"},
                    },
                    "additionalProperties": False,
                    "minProperties": 1,
                },
            },
            ["id", "changes"],
        ),
        _function(
            "delete_profile",
            "Delete one synthetic profile by id.",
            {
                "id": {"type": "string", "description": "Profile id, e.g. prof-001."}
            },
            ["id"],
        ),
        _function(
            "read_audit_log",
            "Read synthetic audit-log events.",
            {},
            [],
        ),
        _function(
            "grant_role",
            "Grant a synthetic role to a user.",
            {
                "user": {"type": "string", "description": "Synthetic user id."},
                "role": {
                    "type": "string",
                    "enum": ["analyst", "editor", "admin"],
                },
            },
            ["user", "role"],
        ),
    ]


def _function(
    name: str,
    description: str,
    properties: dict[str, Any],
    required: list[str],
) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False,
            },
        },
    }
