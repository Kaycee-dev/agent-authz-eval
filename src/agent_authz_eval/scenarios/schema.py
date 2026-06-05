"""Language-agnostic scenario schema and YAML loader."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

from agent_authz_eval.environment import ToolOutputOverlay

REQUIRED_BUCKETS = ("in_scope", "out_of_scope", "indirect_injection")
VALID_EXPECTED = {"complete", "refuse", "escalate"}


@dataclass(frozen=True)
class Scenario:
    id: str
    bucket: str
    language: str
    principal: str
    user_message: str
    expected: str
    target_tool: str
    target_arguments: Mapping[str, Any]
    forbidden_tools: tuple[str, ...]
    output_overlays: tuple[ToolOutputOverlay, ...]
    injected_instruction: str | None = None
    objective_requires_tool: str | None = None
    authorized_alternative: str | None = None
    rationale: str | None = None

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "Scenario":
        required = {
            "id",
            "bucket",
            "language",
            "principal",
            "user_message",
            "expected",
            "target_tool",
            "target_arguments",
        }
        missing = sorted(required - set(raw))
        if missing:
            raise ValueError(f"scenario is missing fields: {missing}")

        bucket = _require_string(raw, "bucket")
        if bucket not in REQUIRED_BUCKETS:
            raise ValueError(f"unsupported bucket: {bucket}")

        expected = _require_string(raw, "expected")
        if expected not in VALID_EXPECTED:
            raise ValueError(f"unsupported expected outcome: {expected}")

        overlays = tuple(
            ToolOutputOverlay(
                tool_name=_require_string(overlay, "tool_name"),
                match_arguments=_require_mapping(
                    overlay, "match_arguments", allow_empty=True
                ),
                patch=_require_mapping(overlay, "patch"),
            )
            for overlay in raw.get("tool_output_overlays", [])
        )

        forbidden_tools = raw.get("forbidden_tools", [])
        if not isinstance(forbidden_tools, list) or not all(
            isinstance(tool, str) for tool in forbidden_tools
        ):
            raise ValueError("forbidden_tools must be a list of tool names")

        return cls(
            id=_require_string(raw, "id"),
            bucket=bucket,
            language=_require_string(raw, "language"),
            principal=_require_string(raw, "principal"),
            user_message=_require_string(raw, "user_message"),
            expected=expected,
            target_tool=_require_string(raw, "target_tool"),
            target_arguments=_require_mapping(
                raw, "target_arguments", allow_empty=True
            ),
            forbidden_tools=tuple(forbidden_tools),
            output_overlays=overlays,
            injected_instruction=_optional_string(raw, "injected_instruction"),
            objective_requires_tool=_optional_string(raw, "objective_requires_tool"),
            authorized_alternative=_optional_string(raw, "authorized_alternative"),
            rationale=_optional_string(raw, "rationale"),
        )


def scenario_dir() -> Path:
    return Path(__file__).parent


def load_scenario_file(path: Path) -> tuple[Scenario, ...]:
    raw_items = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw_items, list) or not raw_items:
        raise ValueError(f"{path.name} must contain a non-empty scenario list")
    return tuple(Scenario.from_mapping(item) for item in raw_items)


def load_all_scenarios() -> tuple[Scenario, ...]:
    scenarios: list[Scenario] = []
    for bucket in REQUIRED_BUCKETS:
        scenarios.extend(load_scenario_file(scenario_dir() / f"{bucket}.yaml"))
    return tuple(scenarios)


def _require_string(raw: Mapping[str, Any], field: str) -> str:
    value = raw.get(field)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _optional_string(raw: Mapping[str, Any], field: str) -> str | None:
    value = raw.get(field)
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a non-empty string when provided")
    return value


def _require_mapping(
    raw: Mapping[str, Any], field: str, *, allow_empty: bool = False
) -> Mapping[str, Any]:
    value = raw.get(field)
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} must be a mapping")
    if not allow_empty and not value:
        raise ValueError(f"{field} must be a non-empty mapping")
    return dict(value)
