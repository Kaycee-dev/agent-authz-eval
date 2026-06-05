"""Model adapters for tool-calling pilot runs."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Protocol
from urllib import error, request

from agent_authz_eval.config import (
    OPENWEIGHTS_BASE_URL_ENV,
    OPENWEIGHTS_DEFAULT_BASE_URL,
)


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class ModelResponse:
    content: str
    tool_calls: tuple[ToolCall, ...]
    assistant_message: dict[str, Any]
    raw: dict[str, Any]


class ModelAdapter(Protocol):
    provider: str
    model: str

    def complete(
        self,
        *,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> ModelResponse:
        ...


class OpenAIChatCompletionsAdapter:
    provider = "openai"

    def __init__(
        self,
        *,
        model: str,
        temperature: float,
        api_key_env: str = "OPENAI_API_KEY",
        api_url: str = "https://api.openai.com/v1/chat/completions",
        provider: str = "openai",
        timeout_seconds: int = 120,
        max_retries: int = 2,
        max_tokens: int = 300,
    ) -> None:
        api_key = os.environ.get(api_key_env)
        if not api_key:
            raise RuntimeError(f"{api_key_env} is required for {provider} runs")
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self._api_key = api_key
        self._api_url = api_url
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._max_tokens = max_tokens

    def complete(
        self,
        *,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> ModelResponse:
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            "parallel_tool_calls": False,
            "temperature": self.temperature,
            "max_tokens": self._max_tokens,
        }
        body = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            self._api_url,
            data=body,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        raw = self._post_with_retries(http_request)

        message = raw["choices"][0]["message"]
        tool_calls = tuple(_parse_openai_tool_call(item) for item in message.get("tool_calls", []))
        assistant_message = {
            "role": "assistant",
            "content": message.get("content") or "",
        }
        if message.get("tool_calls"):
            assistant_message["tool_calls"] = message["tool_calls"]

        return ModelResponse(
            content=message.get("content") or "",
            tool_calls=tool_calls,
            assistant_message=assistant_message,
            raw=raw,
        )

    def _post_with_retries(self, http_request: request.Request) -> dict[str, Any]:
        last_error: BaseException | None = None
        for attempt_index in range(self._max_retries + 1):
            try:
                with request.urlopen(
                    http_request, timeout=self._timeout_seconds
                ) as response:
                    return json.loads(response.read().decode("utf-8"))
            except error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                if exc.code in {429, 500, 502, 503, 504} and attempt_index < self._max_retries:
                    time.sleep(2**attempt_index)
                    last_error = exc
                    continue
                raise RuntimeError(
                    f"{self.provider} API returned HTTP {exc.code}: {body[:500]}"
                ) from exc
            except (TimeoutError, error.URLError) as exc:
                last_error = exc
                if attempt_index >= self._max_retries:
                    break
                time.sleep(2**attempt_index)
        raise RuntimeError(f"{self.provider} API request failed after retries") from last_error


class OpenWeightsChatCompletionsAdapter(OpenAIChatCompletionsAdapter):
    """OpenAI-compatible adapter for an open-weights inference host."""

    def __init__(
        self,
        *,
        model: str,
        temperature: float,
        api_key_env: str = "OPENWEIGHTS_API_KEY",
        timeout_seconds: int = 120,
        max_retries: int = 2,
        max_tokens: int = 300,
    ) -> None:
        api_url = os.environ.get(OPENWEIGHTS_BASE_URL_ENV) or OPENWEIGHTS_DEFAULT_BASE_URL
        super().__init__(
            model=model,
            temperature=temperature,
            api_key_env=api_key_env,
            api_url=api_url,
            provider="openweights",
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            max_tokens=max_tokens,
        )


class AnthropicMessagesAdapter:
    provider = "anthropic"

    def __init__(
        self,
        *,
        model: str,
        temperature: float,
        api_key_env: str = "ANTHROPIC_API_KEY",
        timeout_seconds: int = 120,
        max_retries: int = 2,
        max_tokens: int = 300,
    ) -> None:
        api_key = os.environ.get(api_key_env)
        if not api_key:
            raise RuntimeError(f"{api_key_env} is required for Anthropic runs")
        self.model = model
        self.temperature = temperature
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._max_tokens = max_tokens

    def complete(
        self,
        *,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> ModelResponse:
        system, anthropic_messages = _to_anthropic_messages(messages)
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": anthropic_messages,
            "tools": _to_anthropic_tools(tools),
            "temperature": self.temperature,
            "max_tokens": self._max_tokens,
        }
        if system:
            payload["system"] = system
        body = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            "https://api.anthropic.com/v1/messages",
            data=body,
            headers={
                "x-api-key": self._api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        raw = self._post_with_retries(http_request)
        return _parse_anthropic_response(raw)

    def _post_with_retries(self, http_request: request.Request) -> dict[str, Any]:
        last_error: BaseException | None = None
        for attempt_index in range(self._max_retries + 1):
            try:
                with request.urlopen(
                    http_request, timeout=self._timeout_seconds
                ) as response:
                    return json.loads(response.read().decode("utf-8"))
            except error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                if exc.code in {429, 500, 502, 503, 504} and attempt_index < self._max_retries:
                    time.sleep(2**attempt_index)
                    last_error = exc
                    continue
                raise RuntimeError(
                    f"Anthropic API returned HTTP {exc.code}: {body[:500]}"
                ) from exc
            except (TimeoutError, error.URLError) as exc:
                last_error = exc
                if attempt_index >= self._max_retries:
                    break
                time.sleep(2**attempt_index)
        raise RuntimeError("Anthropic API request failed after retries") from last_error


class ScriptedModelAdapter:
    """Deterministic adapter for runner tests; never used for public metrics."""

    provider = "scripted"

    def __init__(self, responses: list[ModelResponse], model: str = "scripted-test") -> None:
        self.model = model
        self._responses = list(responses)

    def complete(
        self,
        *,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> ModelResponse:
        if not self._responses:
            raise RuntimeError("scripted adapter has no remaining responses")
        return self._responses.pop(0)


def make_model_adapter(
    *,
    provider: str,
    model: str,
    temperature: float,
) -> ModelAdapter:
    if provider == "openai":
        return OpenAIChatCompletionsAdapter(model=model, temperature=temperature)
    if provider == "anthropic":
        return AnthropicMessagesAdapter(model=model, temperature=temperature)
    if provider == "openweights":
        return OpenWeightsChatCompletionsAdapter(model=model, temperature=temperature)
    raise ValueError(f"unsupported provider: {provider}")


def make_tool_response(
    *,
    tool_call_id: str,
    tool_name: str,
    arguments: dict[str, Any],
) -> ModelResponse:
    arguments_json = json.dumps(arguments)
    raw_tool_call = {
        "id": tool_call_id,
        "type": "function",
        "function": {"name": tool_name, "arguments": arguments_json},
    }
    return ModelResponse(
        content="",
        tool_calls=(ToolCall(id=tool_call_id, name=tool_name, arguments=arguments),),
        assistant_message={
            "role": "assistant",
            "content": "",
            "tool_calls": [raw_tool_call],
        },
        raw={"scripted": True},
    )


def make_text_response(content: str) -> ModelResponse:
    return ModelResponse(
        content=content,
        tool_calls=(),
        assistant_message={"role": "assistant", "content": content},
        raw={"scripted": True},
    )


def _parse_openai_tool_call(raw_tool_call: dict[str, Any]) -> ToolCall:
    arguments_text = raw_tool_call.get("function", {}).get("arguments") or "{}"
    try:
        arguments = json.loads(arguments_text)
    except json.JSONDecodeError:
        arguments = {"_invalid_json_arguments": arguments_text}
    if not isinstance(arguments, dict):
        arguments = {"_non_object_arguments": arguments}

    return ToolCall(
        id=raw_tool_call["id"],
        name=raw_tool_call["function"]["name"],
        arguments=arguments,
    )


def _to_anthropic_tools(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    converted = []
    for tool in tools:
        function = tool["function"]
        converted.append(
            {
                "name": function["name"],
                "description": function.get("description", ""),
                "input_schema": function["parameters"],
            }
        )
    return converted


def _to_anthropic_messages(
    messages: list[dict[str, Any]]
) -> tuple[str | None, list[dict[str, Any]]]:
    system_parts: list[str] = []
    converted: list[dict[str, Any]] = []
    pending_tool_results: list[dict[str, Any]] = []

    for message in messages:
        role = message["role"]
        if role == "system":
            system_parts.append(message.get("content") or "")
            continue

        if role == "tool":
            pending_tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": message["tool_call_id"],
                    "content": message.get("content") or "",
                }
            )
            continue

        if pending_tool_results:
            converted.append({"role": "user", "content": pending_tool_results})
            pending_tool_results = []

        if role == "user":
            converted.append({"role": "user", "content": message.get("content") or ""})
        elif role == "assistant":
            converted.append({"role": "assistant", "content": _assistant_blocks(message)})
        else:
            raise ValueError(f"unsupported message role for Anthropic: {role}")

    if pending_tool_results:
        converted.append({"role": "user", "content": pending_tool_results})

    system = "\n\n".join(part for part in system_parts if part)
    return system or None, converted


def _assistant_blocks(message: dict[str, Any]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    content = message.get("content") or ""
    if content:
        blocks.append({"type": "text", "text": content})
    for raw_tool_call in message.get("tool_calls", []):
        parsed = _parse_openai_tool_call(raw_tool_call)
        blocks.append(
            {
                "type": "tool_use",
                "id": parsed.id,
                "name": parsed.name,
                "input": parsed.arguments,
            }
        )
    return blocks


def _parse_anthropic_response(raw: dict[str, Any]) -> ModelResponse:
    text_parts: list[str] = []
    raw_tool_calls: list[dict[str, Any]] = []
    tool_calls: list[ToolCall] = []
    for block in raw.get("content", []):
        if block.get("type") == "text":
            text_parts.append(block.get("text") or "")
        elif block.get("type") == "tool_use":
            arguments = block.get("input") or {}
            if not isinstance(arguments, dict):
                arguments = {"_non_object_arguments": arguments}
            tool_call = ToolCall(
                id=block["id"],
                name=block["name"],
                arguments=arguments,
            )
            tool_calls.append(tool_call)
            raw_tool_calls.append(
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.name,
                        "arguments": json.dumps(tool_call.arguments),
                    },
                }
            )

    content = "\n".join(part for part in text_parts if part)
    assistant_message: dict[str, Any] = {"role": "assistant", "content": content}
    if raw_tool_calls:
        assistant_message["tool_calls"] = raw_tool_calls
    return ModelResponse(
        content=content,
        tool_calls=tuple(tool_calls),
        assistant_message=assistant_message,
        raw=raw,
    )
