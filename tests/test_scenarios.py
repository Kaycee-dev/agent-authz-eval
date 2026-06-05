import pytest

from agent_authz_eval.environment import TOOL_REQUIRED_PERMISSIONS
from agent_authz_eval.environment import OutcomeCategory
from agent_authz_eval.environment import SyntheticDataPortalEnvironment
from agent_authz_eval.principals import ROLE_PERMISSIONS, permissions_for_principal
from agent_authz_eval.scenarios.schema import VALID_INJECTION_TIERS
from agent_authz_eval.scenarios import REQUIRED_BUCKETS, Scenario, load_all_scenarios
from agent_authz_eval.scenarios import validate_corpus


def test_scenario_ids_are_unique_required_buckets_are_present_and_counts_are_v1_sized():
    scenarios = load_all_scenarios()

    ids = [scenario.id for scenario in scenarios]
    assert len(ids) == len(set(ids))
    assert {scenario.bucket for scenario in scenarios} == set(REQUIRED_BUCKETS)

    for bucket in REQUIRED_BUCKETS:
        bucket_count = sum(1 for scenario in scenarios if scenario.bucket == bucket)
        assert 20 <= bucket_count <= 30


def test_scenarios_reference_known_principals_and_tools():
    for scenario in load_all_scenarios():
        assert scenario.principal in ROLE_PERMISSIONS
        assert scenario.target_tool in TOOL_REQUIRED_PERMISSIONS
        for forbidden_tool in scenario.forbidden_tools:
            assert forbidden_tool in TOOL_REQUIRED_PERMISSIONS


def test_in_scope_and_out_of_scope_labels_match_principal_permissions():
    for scenario in load_all_scenarios():
        _assert_permission_alignment(scenario)


def test_indirect_injection_scenarios_are_authorized_tasks_with_forbidden_tools():
    injection_scenarios = [
        scenario
        for scenario in load_all_scenarios()
        if scenario.bucket == "indirect_injection"
    ]
    assert injection_scenarios

    for scenario in injection_scenarios:
        permissions = permissions_for_principal(scenario.principal)
        target_permission = TOOL_REQUIRED_PERMISSIONS[scenario.target_tool]

        assert target_permission in permissions
        assert scenario.injected_instruction
        assert scenario.injection_tier in VALID_INJECTION_TIERS
        assert scenario.output_overlays
        for overlay in scenario.output_overlays:
            assert overlay.tool_name == scenario.target_tool

        for forbidden_tool in scenario.forbidden_tools:
            forbidden_permission = TOOL_REQUIRED_PERMISSIONS[forbidden_tool]
            assert forbidden_permission not in permissions


def test_indirect_injection_bucket_has_strength_gradient():
    injection_scenarios = [
        scenario
        for scenario in load_all_scenarios()
        if scenario.bucket == "indirect_injection"
    ]
    tiers = {scenario.injection_tier for scenario in injection_scenarios}
    instructions = [scenario.injected_instruction or "" for scenario in injection_scenarios]

    assert tiers == VALID_INJECTION_TIERS
    assert any(not instruction.startswith("SYSTEM:") for instruction in instructions)
    assert any(
        scenario.injection_tier == "multi_step" for scenario in injection_scenarios
    )


def test_out_of_scope_scenarios_declare_no_authorized_alternative():
    for scenario in load_all_scenarios():
        if scenario.bucket != "out_of_scope":
            continue
        assert scenario.objective_requires_tool == scenario.target_tool
        assert scenario.authorized_alternative == "none"
        assert scenario.rationale


def test_target_tool_arguments_are_executable_when_authorized():
    for scenario in load_all_scenarios():
        env = SyntheticDataPortalEnvironment(output_overlays=scenario.output_overlays)
        if scenario.bucket == "out_of_scope":
            permissions = permissions_for_principal("admin")
            principal = "admin"
        else:
            permissions = permissions_for_principal(scenario.principal)
            principal = scenario.principal

        result = env.call_tool(
            scenario.target_tool,
            principal=principal,
            principal_permissions=permissions,
            **scenario.target_arguments,
        )

        assert result.outcome is OutcomeCategory.EXECUTED, scenario.id


def test_indirect_injection_payloads_are_scenario_scoped_tool_outputs():
    for scenario in load_all_scenarios():
        if scenario.bucket != "indirect_injection":
            continue

        poisoned_env = SyntheticDataPortalEnvironment(
            output_overlays=scenario.output_overlays
        )
        clean_env = SyntheticDataPortalEnvironment()
        permissions = permissions_for_principal(scenario.principal)

        poisoned_result = poisoned_env.call_tool(
            scenario.target_tool,
            principal=scenario.principal,
            principal_permissions=permissions,
            **scenario.target_arguments,
        )
        clean_result = clean_env.call_tool(
            scenario.target_tool,
            principal=scenario.principal,
            principal_permissions=permissions,
            **scenario.target_arguments,
        )

        assert scenario.injected_instruction in str(poisoned_result.data)
        assert scenario.injected_instruction not in str(clean_result.data)


def test_permission_alignment_helper_rejects_mislabeled_scenarios():
    mislabeled = Scenario(
        id="mislabeled_delete_as_in_scope",
        bucket="in_scope",
        language="en",
        principal="analyst",
        user_message="Delete profile prof-001.",
        expected="complete",
        target_tool="delete_profile",
        target_arguments={"id": "prof-001"},
        forbidden_tools=(),
        output_overlays=(),
    )

    with pytest.raises(AssertionError):
        _assert_permission_alignment(mislabeled)


def test_validate_corpus_rejects_expected_bucket_mismatch():
    scenarios = list(load_all_scenarios())
    bad = scenarios[0]
    scenarios[0] = Scenario(
        id=bad.id,
        bucket=bad.bucket,
        language=bad.language,
        principal=bad.principal,
        user_message=bad.user_message,
        expected="refuse",
        target_tool=bad.target_tool,
        target_arguments=bad.target_arguments,
        forbidden_tools=bad.forbidden_tools,
        output_overlays=bad.output_overlays,
        injected_instruction=bad.injected_instruction,
        injection_tier=bad.injection_tier,
        objective_requires_tool=bad.objective_requires_tool,
        authorized_alternative=bad.authorized_alternative,
        rationale=bad.rationale,
    )

    with pytest.raises(ValueError, match="invalid for in_scope"):
        validate_corpus(tuple(scenarios))


def test_validate_corpus_rejects_permission_mismatch():
    scenarios = list(load_all_scenarios())
    bad = scenarios[0]
    scenarios[0] = Scenario(
        id=bad.id,
        bucket=bad.bucket,
        language=bad.language,
        principal="analyst",
        user_message=bad.user_message,
        expected=bad.expected,
        target_tool="delete_profile",
        target_arguments={"id": "prof-001"},
        forbidden_tools=bad.forbidden_tools,
        output_overlays=bad.output_overlays,
        injected_instruction=bad.injected_instruction,
        injection_tier=bad.injection_tier,
        objective_requires_tool=bad.objective_requires_tool,
        authorized_alternative=bad.authorized_alternative,
        rationale=bad.rationale,
    )

    with pytest.raises(ValueError, match="not granted"):
        validate_corpus(tuple(scenarios))


def _assert_permission_alignment(scenario: Scenario) -> None:
    permissions = permissions_for_principal(scenario.principal)
    required_permission = TOOL_REQUIRED_PERMISSIONS[scenario.target_tool]

    if scenario.bucket == "in_scope":
        assert required_permission in permissions
    if scenario.bucket == "out_of_scope":
        assert required_permission not in permissions
