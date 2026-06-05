"""Pinned pilot configuration."""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_PILOT_PROVIDER = "openai"
DEFAULT_PILOT_MODEL = "gpt-4.1-nano-2025-04-14"
CONTEXT_ONLY = "context_only"
AUTHZ_POLICY = "authz_policy"
AUTHZ_POLICY_WITH_INJECTION_GUARD = "authz_policy_with_injection_guard"
CONDITIONS = (
    CONTEXT_ONLY,
    AUTHZ_POLICY,
    AUTHZ_POLICY_WITH_INJECTION_GUARD,
)

DEFAULT_CONDITION = AUTHZ_POLICY
DEFAULT_TEMPERATURE = 0.0
DEFAULT_MAX_TOOL_ROUNDS = 3


@dataclass(frozen=True)
class PilotConfig:
    provider: str = DEFAULT_PILOT_PROVIDER
    model: str = DEFAULT_PILOT_MODEL
    condition: str = DEFAULT_CONDITION
    temperature: float = DEFAULT_TEMPERATURE
    max_tool_rounds: int = DEFAULT_MAX_TOOL_ROUNDS
