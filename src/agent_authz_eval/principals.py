"""Principal and role permissions for scenario execution.

This module is the single source of truth for permission sets passed into the
mock environment. Runners and tests should call `permissions_for_principal`
rather than duplicating role grants.
"""

from __future__ import annotations

from types import MappingProxyType

from agent_authz_eval.environment import TOOL_REQUIRED_PERMISSIONS

ALL_PERMISSIONS = frozenset(TOOL_REQUIRED_PERMISSIONS.values())

ROLE_PERMISSIONS = MappingProxyType(
    {
        "analyst": frozenset({"profile:read", "audit:read"}),
        "editor": frozenset({"profile:read", "profile:write", "profile:export"}),
        "admin": ALL_PERMISSIONS,
    }
)


def permissions_for_principal(principal: str) -> frozenset[str]:
    try:
        return ROLE_PERMISSIONS[principal]
    except KeyError as exc:
        raise KeyError(f"unknown principal: {principal}") from exc
