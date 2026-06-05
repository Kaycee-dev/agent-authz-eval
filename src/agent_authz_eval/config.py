"""Pinned pilot configuration."""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_PILOT_PROVIDER = "openai"
DEFAULT_PILOT_MODEL = "gpt-4.1-nano-2025-04-14"
DEFAULT_CONDITION = "explicit"
DEFAULT_TEMPERATURE = 0.0
DEFAULT_MAX_TOOL_ROUNDS = 3


@dataclass(frozen=True)
class PilotConfig:
    provider: str = DEFAULT_PILOT_PROVIDER
    model: str = DEFAULT_PILOT_MODEL
    condition: str = DEFAULT_CONDITION
    temperature: float = DEFAULT_TEMPERATURE
    max_tool_rounds: int = DEFAULT_MAX_TOOL_ROUNDS
