"""Pinned pilot configuration."""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_PILOT_PROVIDER = "openai"
OPENAI_FULL_MATRIX_MODEL = "gpt-4.1-mini-2025-04-14"
ANTHROPIC_FULL_MATRIX_MODEL = "claude-3-5-haiku-20241022"
GROQ_FULL_MATRIX_MODEL = "llama-3.3-70b-versatile"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
FULL_MATRIX_TEMPERATURE = 0.7
FULL_MATRIX_N = 5

FULL_MATRIX_MODELS = {
    "openai": OPENAI_FULL_MATRIX_MODEL,
    "anthropic": ANTHROPIC_FULL_MATRIX_MODEL,
    "groq": GROQ_FULL_MATRIX_MODEL,
}

DEFAULT_PILOT_MODEL = OPENAI_FULL_MATRIX_MODEL
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
