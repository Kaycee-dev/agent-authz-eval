"""Model adapters for tool-calling pilot runs."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Protocol
from urllib import request


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
        timeout_seconds: int = 60,
    ) -> None:
        api_key = os.environ.get(api_key_env)
        if not api_key:
            raise RuntimeError(f"{api_key_env} is required for OpenAI pilot runs")
        self.model = model
        self.temperature = temperature
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds

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
        }
        body = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with request.urlopen(http_request, timeout=self._timeout_seconds) as response:
            raw = json.loads(response.read().decode("utf-8"))

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
