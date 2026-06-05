"""Synthetic least-privilege agent authorization evaluation."""

from agent_authz_eval.environment import (
    DEFAULT_SEED,
    TOOL_REQUIRED_PERMISSIONS,
    OutcomeCategory,
    SyntheticDataPortalEnvironment,
    ToolAttempt,
    ToolOutputOverlay,
    ToolResult,
)
from agent_authz_eval.principals import (
    ALL_PERMISSIONS,
    ROLE_PERMISSIONS,
    permissions_for_principal,
)

__all__ = [
    "DEFAULT_SEED",
    "TOOL_REQUIRED_PERMISSIONS",
    "OutcomeCategory",
    "SyntheticDataPortalEnvironment",
    "ToolAttempt",
    "ToolOutputOverlay",
    "ToolResult",
    "ALL_PERMISSIONS",
    "ROLE_PERMISSIONS",
    "permissions_for_principal",
]
