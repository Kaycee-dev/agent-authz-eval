import io
import json
from http.client import RemoteDisconnected
from urllib import error, request

import pytest

from agent_authz_eval.config import AUTHZ_POLICY, PilotConfig
from agent_authz_eval.metrics import compute_pilot_metrics
from agent_authz_eval.models import (
    ModelAPIError,
    OpenAIChatCompletionsAdapter,
    make_text_response,
)
from agent_authz_eval.runner import (
    append_jsonl_record,
    load_jsonl_records,
    run_pilot,
)
from agent_authz_eval.scenarios import Scenario


class CountingTextAdapter:
    provider = "scripted"
    model = "resume-test-model"

    def __init__(self, *, crash_on_call=None, error=None):
        self.calls = 0
        self.crash_on_call = crash_on_call
        self.error = error

    def complete(self, *, messages, tools):
        self.calls += 1
        if self.crash_on_call == self.calls:
            raise KeyboardInterrupt("simulated process interruption")
        if self.error is not None:
            raise self.error
        return make_text_response("done")


def test_mid_run_crash_resumes_only_missing_units(tmp_path):
    path = tmp_path / "resume.jsonl"
    scenarios = tuple(_scenario(index) for index in range(1, 6))
    config = PilotConfig(
        provider="scripted",
        model="resume-test-model",
        condition=AUTHZ_POLICY,
    )
    first_adapter = CountingTextAdapter(crash_on_call=3)

    with pytest.raises(KeyboardInterrupt):
        run_pilot(
            adapter=first_adapter,
            scenarios=scenarios,
            config=config,
            n=1,
            validate=False,
            record_sink=lambda record: append_jsonl_record(path, record),
        )

    first_records = load_jsonl_records(path, repair_trailing=True)
    assert len(first_records) == 2
    completed_keys = {record["run_unit_key"] for record in first_records}

    second_adapter = CountingTextAdapter()
    second_records = run_pilot(
        adapter=second_adapter,
        scenarios=scenarios,
        config=config,
        n=1,
        validate=False,
        completed_keys=completed_keys,
        record_sink=lambda record: append_jsonl_record(path, record),
    )

    all_records = load_jsonl_records(path, repair_trailing=True)
    assert second_adapter.calls == 3
    assert len(second_records) == 3
    assert len(all_records) == 5
    assert len({record["run_unit_key"] for record in all_records}) == 5


def test_truncated_trailing_line_is_repaired_and_key_is_rerun(tmp_path):
    path = tmp_path / "truncated.jsonl"
    complete = {"run_unit_key": "complete", "record_status": "ok"}
    path.write_text(json.dumps(complete) + "\n{\"run_unit_key\":", encoding="utf-8")

    records = load_jsonl_records(path, repair_trailing=True)
    append_jsonl_record(path, {"run_unit_key": "rerun", "record_status": "ok"})

    assert records == [complete]
    assert [record["run_unit_key"] for record in load_jsonl_records(path)] == [
        "complete",
        "rerun",
    ]


def test_connection_error_retries_then_succeeds(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    adapter = OpenAIChatCompletionsAdapter(
        model="test-model",
        temperature=0.7,
        max_retries=2,
        max_backoff_seconds=0,
    )
    calls = 0

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self):
            return b'{"choices":[]}'

    def fake_urlopen(http_request, timeout):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RemoteDisconnected("closed")
        return Response()

    monkeypatch.setattr(request, "urlopen", fake_urlopen)

    assert adapter._post_with_retries(request.Request("https://example.invalid")) == {
        "choices": []
    }
    assert calls == 2


def test_retryable_http_5xx_retries_then_succeeds(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    adapter = OpenAIChatCompletionsAdapter(
        model="test-model",
        temperature=0.7,
        max_retries=2,
        max_backoff_seconds=0,
    )
    calls = 0

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self):
            return b'{"choices":[]}'

    def fake_urlopen(http_request, timeout):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise error.HTTPError(
                http_request.full_url,
                503,
                "unavailable",
                hdrs=None,
                fp=io.BytesIO(b'{"error":"unavailable"}'),
            )
        return Response()

    monkeypatch.setattr(request, "urlopen", fake_urlopen)

    assert adapter._post_with_retries(request.Request("https://example.invalid")) == {
        "choices": []
    }
    assert calls == 2


def test_non_retryable_http_error_fails_fast(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    adapter = OpenAIChatCompletionsAdapter(
        model="test-model",
        temperature=0.7,
        max_retries=3,
        max_backoff_seconds=0,
    )
    calls = 0

    def fake_urlopen(http_request, timeout):
        nonlocal calls
        calls += 1
        raise error.HTTPError(
            http_request.full_url,
            400,
            "bad request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":"bad request"}'),
        )

    monkeypatch.setattr(request, "urlopen", fake_urlopen)

    with pytest.raises(ModelAPIError) as caught:
        adapter._post_with_retries(request.Request("https://example.invalid"))

    assert calls == 1
    assert caught.value.retryable is False
    assert caught.value.status_code == 400
    assert caught.value.attempt_count == 1


def test_terminal_api_error_is_recorded_and_matrix_continues():
    terminal_error = ModelAPIError(
        "retry budget exhausted",
        category="connection_error",
        retryable=True,
        attempt_count=3,
    )
    adapter = CountingTextAdapter(error=terminal_error)
    records = run_pilot(
        adapter=adapter,
        scenarios=(_scenario(1), _scenario(2)),
        config=PilotConfig(
            provider="scripted",
            model="resume-test-model",
            condition=AUTHZ_POLICY,
        ),
        n=1,
        validate=False,
    )

    assert adapter.calls == 2
    assert len(records) == 2
    assert all(record["record_status"] == "error" for record in records)
    assert all(record["error"]["category"] == "connection_error" for record in records)
    assert all(record["error"]["attempt_count"] == 3 for record in records)


def test_error_records_are_excluded_from_behavior_metrics():
    records = [
        {
            "record_status": "ok",
            "scenario": {"bucket": "out_of_scope", "principal": "analyst"},
            "attempts": [{"is_denied_authz_event": False}],
            "classification": {"target_executed": False},
        },
        {
            "record_status": "error",
            "scenario": {"bucket": "out_of_scope", "principal": "analyst"},
            "attempts": [{"is_denied_authz_event": True}],
            "classification": None,
            "error": {"category": "connection_error"},
        },
    ]

    metrics = compute_pilot_metrics(records)

    assert metrics["total_runs"] == 2
    assert metrics["valid_runs"] == 1
    assert metrics["error_runs"] == 1
    assert metrics["out_of_scope_runs"] == 1
    assert metrics["ocr"] == 0.0


def _scenario(index):
    return Scenario(
        id=f"resume_{index}",
        bucket="in_scope",
        language="en",
        principal="analyst",
        user_message=f"Read profile prof-00{index}.",
        expected="complete",
        target_tool="read_profile",
        target_arguments={"id": "prof-001"},
        forbidden_tools=(),
        output_overlays=(),
    )
