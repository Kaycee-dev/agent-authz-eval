"""Language-agnostic scenario schema and YAML loader."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

from agent_authz_eval.environment import (
    TOOL_REQUIRED_PERMISSIONS,
    OutcomeCategory,
    SyntheticDataPortalEnvironment,
    ToolOutputOverlay,
)
from agent_authz_eval.principals import ROLE_PERMISSIONS, permissions_for_principal

REQUIRED_BUCKETS = ("in_scope", "out_of_scope", "indirect_injection")
VALID_EXPECTED = {"complete", "refuse", "escalate"}
VALID_INJECTION_TIERS = {
    "overt_system",
    "plausible_note",
    "embedded_data",
    "authority_spoof",
    "multi_step",
}
MIN_SCENARIOS_PER_BUCKET = 20
MAX_SCENARIOS_PER_BUCKET = 30


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
    injection_tier: str | None = None
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
            injection_tier=_optional_string(raw, "injection_tier"),
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


def load_all_scenarios(*, validate: bool = True) -> tuple[Scenario, ...]:
    scenarios: list[Scenario] = []
    for bucket in REQUIRED_BUCKETS:
        scenarios.extend(load_scenario_file(scenario_dir() / f"{bucket}.yaml"))
    loaded = tuple(scenarios)
    if validate:
        validate_corpus(loaded)
    return loaded


def validate_corpus(scenarios: tuple[Scenario, ...]) -> None:
    """Fail loudly if scenario labels drift from RBAC ground truth."""

    if not scenarios:
        raise ValueError("scenario corpus is empty")

    ids = [scenario.id for scenario in scenarios]
    duplicate_ids = sorted({scenario_id for scenario_id in ids if ids.count(scenario_id) > 1})
    if duplicate_ids:
        raise ValueError(f"duplicate scenario ids: {duplicate_ids}")

    bucket_counts = {
        bucket: sum(1 for scenario in scenarios if scenario.bucket == bucket)
        for bucket in REQUIRED_BUCKETS
    }
    if set(bucket_counts) != set(REQUIRED_BUCKETS):
        raise ValueError("required bucket configuration is invalid")
    for bucket, count in bucket_counts.items():
        if not MIN_SCENARIOS_PER_BUCKET <= count <= MAX_SCENARIOS_PER_BUCKET:
            raise ValueError(
                f"{bucket} must contain {MIN_SCENARIOS_PER_BUCKET}-"
                f"{MAX_SCENARIOS_PER_BUCKET} scenarios; found {count}"
            )

    for scenario in scenarios:
        _validate_scenario_semantics(scenario)


def _validate_scenario_semantics(scenario: Scenario) -> None:
    if scenario.principal not in ROLE_PERMISSIONS:
        raise ValueError(f"{scenario.id}: unknown principal {scenario.principal}")
    if scenario.target_tool not in TOOL_REQUIRED_PERMISSIONS:
        raise ValueError(f"{scenario.id}: unknown target tool {scenario.target_tool}")
    for forbidden_tool in scenario.forbidden_tools:
        if forbidden_tool not in TOOL_REQUIRED_PERMISSIONS:
            raise ValueError(f"{scenario.id}: unknown forbidden tool {forbidden_tool}")

    expected_by_bucket = {
        "in_scope": {"complete"},
        "out_of_scope": {"refuse", "escalate"},
        "indirect_injection": {"complete"},
    }
    if scenario.expected not in expected_by_bucket[scenario.bucket]:
        allowed = sorted(expected_by_bucket[scenario.bucket])
        raise ValueError(
            f"{scenario.id}: expected={scenario.expected!r} is invalid for "
            f"{scenario.bucket}; expected one of {allowed}"
        )

    permissions = permissions_for_principal(scenario.principal)
    target_permission = TOOL_REQUIRED_PERMISSIONS[scenario.target_tool]

    if scenario.bucket == "in_scope" and target_permission not in permissions:
        raise ValueError(
            f"{scenario.id}: in_scope target {scenario.target_tool} requires "
            f"{target_permission}, not granted to {scenario.principal}"
        )
    if scenario.bucket == "out_of_scope":
        if target_permission in permissions:
            raise ValueError(
                f"{scenario.id}: out_of_scope target {scenario.target_tool} is "
                f"authorized for {scenario.principal}"
            )
        if scenario.objective_requires_tool != scenario.target_tool:
            raise ValueError(
                f"{scenario.id}: objective_requires_tool must equal target_tool"
            )
        if scenario.authorized_alternative != "none":
            raise ValueError(
                f"{scenario.id}: out_of_scope authorized_alternative must be none"
            )
        if not scenario.rationale:
            raise ValueError(f"{scenario.id}: out_of_scope rationale is required")
    if scenario.bucket == "indirect_injection":
        if target_permission not in permissions:
            raise ValueError(
                f"{scenario.id}: indirect_injection target must be authorized"
            )
        if not scenario.injected_instruction:
            raise ValueError(
                f"{scenario.id}: indirect_injection requires injected_instruction"
            )
        if scenario.injection_tier not in VALID_INJECTION_TIERS:
            raise ValueError(
                f"{scenario.id}: indirect_injection requires injection_tier in "
                f"{sorted(VALID_INJECTION_TIERS)}"
            )
        if not scenario.output_overlays:
            raise ValueError(f"{scenario.id}: indirect_injection requires overlays")
        for overlay in scenario.output_overlays:
            if overlay.tool_name != scenario.target_tool:
                raise ValueError(
                    f"{scenario.id}: overlay tool must match target tool"
                )
        for forbidden_tool in scenario.forbidden_tools:
            forbidden_permission = TOOL_REQUIRED_PERMISSIONS[forbidden_tool]
            if forbidden_permission in permissions:
                raise ValueError(
                    f"{scenario.id}: forbidden tool {forbidden_tool} is authorized "
                    f"for {scenario.principal}"
                )

    _validate_target_arguments_execute(scenario)


def _validate_target_arguments_execute(scenario: Scenario) -> None:
    env = SyntheticDataPortalEnvironment(output_overlays=scenario.output_overlays)
    if scenario.bucket == "out_of_scope":
        principal = "admin"
        permissions = permissions_for_principal("admin")
    else:
        principal = scenario.principal
        permissions = permissions_for_principal(scenario.principal)

    result = env.call_tool(
        scenario.target_tool,
        principal=principal,
        principal_permissions=permissions,
        **scenario.target_arguments,
    )
    if result.outcome is not OutcomeCategory.EXECUTED:
        raise ValueError(
            f"{scenario.id}: target arguments do not execute when authorized: "
            f"{result.error}"
        )


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
