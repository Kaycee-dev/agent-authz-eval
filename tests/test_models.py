import json

import pytest

from agent_authz_eval.config import (
    OPENROUTER_API_BASE_URL,
    OPENROUTER_API_URL,
    OPENROUTER_FULL_MATRIX_MODEL,
)
from agent_authz_eval.models import (
    OpenRouterChatCompletionsAdapter,
    make_model_adapter,
)


def test_openrouter_factory_returns_adapter(monkeypatch):
    monkeypatch.setenv("OPENWEIGHTS_API_KEY", "test-openrouter")

    adapter = make_model_adapter(
        provider="openrouter",
        model=OPENROUTER_FULL_MATRIX_MODEL,
        temperature=0.7,
    )

    assert isinstance(adapter, OpenRouterChatCompletionsAdapter)
    assert adapter.provider == "openrouter"


def test_openrouter_adapter_uses_correct_base_url(monkeypatch):
    monkeypatch.setenv("OPENWEIGHTS_API_KEY", "test-openrouter")

    adapter = OpenRouterChatCompletionsAdapter(temperature=0.7)

    assert OPENROUTER_API_BASE_URL == "https://openrouter.ai/api/v1"
    assert adapter._api_url == OPENROUTER_API_URL
    assert adapter._api_url == "https://openrouter.ai/api/v1/chat/completions"


def test_openrouter_adapter_reads_openweights_key_not_groq(monkeypatch):
    monkeypatch.delenv("OPENWEIGHTS_API_KEY", raising=False)
    monkeypatch.setenv("GROQ_API_KEY", "test-groq")

    with pytest.raises(RuntimeError, match="OPENWEIGHTS_API_KEY is required"):
        OpenRouterChatCompletionsAdapter(temperature=0.7)

    monkeypatch.setenv("OPENWEIGHTS_API_KEY", "test-openrouter")
    adapter = OpenRouterChatCompletionsAdapter(temperature=0.7)

    assert adapter._api_key == "test-openrouter"


def test_openrouter_attribution_headers_present(monkeypatch):
    monkeypatch.setenv("OPENWEIGHTS_API_KEY", "test-openrouter")
    adapter = OpenRouterChatCompletionsAdapter(temperature=0.7)
    seen = {}

    def fake_post(http_request):
        seen["url"] = http_request.full_url
        seen["headers"] = dict(http_request.header_items())
        seen["payload"] = json.loads(http_request.data.decode("utf-8"))
        return {"choices": [{"message": {"content": "ok"}}]}

    monkeypatch.setattr(adapter, "_post_with_retries", fake_post)

    adapter.complete(
        messages=[{"role": "user", "content": "ping"}],
        tools=[],
    )

    assert seen["url"] == "https://openrouter.ai/api/v1/chat/completions"
    assert seen["headers"]["Http-referer"] == (
        "https://github.com/Kaycee-dev/agent-authz-eval"
    )
    assert seen["headers"]["X-title"] == "agent-authz-eval"
    assert seen["payload"]["model"] == OPENROUTER_FULL_MATRIX_MODEL


def test_openrouter_default_model(monkeypatch):
    monkeypatch.setenv("OPENWEIGHTS_API_KEY", "test-openrouter")

    adapter = OpenRouterChatCompletionsAdapter(temperature=0.7)

    assert adapter.model == "meta-llama/llama-3.3-70b-instruct"
