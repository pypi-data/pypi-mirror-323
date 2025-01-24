import json

import pytest

from vercel_ai.adapter.parts import (
    TokenUsage,
    Text,
    ToolCall,
    ToolResult,
    StepStart,
    StepFinish,
    Finish,
)
from vercel_ai.adapter.manager import (
    ToolManager,
    UsageManager,
    CompletionManager,
)


def test_toolmanager_used():
    tool_manager = ToolManager(id="1", name="example_tool", buffer='{"key": "value"}')
    assert tool_manager.used is True

    tool_manager = ToolManager(id="", name="", buffer="")
    assert tool_manager.used is False


def test_toolmanager_parsed_buffer():
    tool_manager = ToolManager(id="1", name="example_tool", buffer='{"key": "value"}')
    assert tool_manager.parsed_buffer == {"key": "value"}

    tool_manager = ToolManager(id="1", name="example_tool", buffer="invalid json")
    with pytest.raises(json.JSONDecodeError):
        tool_manager.parsed_buffer


def test_toolmanager_call_part():
    tool_manager = ToolManager(id="1", name="example_tool", buffer='{"key": "value"}')
    tool_call_part = tool_manager.call_part()
    assert isinstance(tool_call_part, ToolCall)
    assert tool_call_part.id == "1"
    assert tool_call_part.name == "example_tool"
    assert tool_call_part.args == {"key": "value"}


def test_toolmanager_result_part():
    tool_manager = ToolManager(id="1", name="example_tool", buffer='{"key": "value"}')
    result_part = tool_manager.result_part(result={"result_key": "result_value"})
    assert isinstance(result_part, ToolResult)
    assert result_part.tool_call_id == "1"
    assert result_part.result == {"result_key": "result_value"}


def test_usagemanager_as_dict():
    usage_manager = UsageManager(completion=20, prompt=10, total=30)
    assert usage_manager.as_dict() == {
        "completionTokens": 20,
        "promptTokens": 10,
        "totalTokens": 30,
    }


def test_usagemanager_as_part():
    usage_manager = UsageManager(completion=20, prompt=10, total=30)
    usage_part = usage_manager.as_part()
    assert isinstance(usage_part, TokenUsage)
    assert usage_part.model_dump(by_alias=True) == {
        "promptTokens": 10,
        "completionTokens": 20,
        "totalTokens": 30,
    }


def test_completionmanager_text_part():
    completion_manager = CompletionManager()
    text_part = completion_manager.text_part("Hello")
    assert isinstance(text_part, Text)
    assert text_part.text_delta == "Hello"
    assert completion_manager.buffer == "Hello"


def test_completionmanager_step_start_part():
    completion_manager = CompletionManager()
    step_start_part = completion_manager.step_start_part("msg123")
    assert isinstance(step_start_part, StepStart)
    assert step_start_part.message_id == "msg123"


def test_completionmanager_step_finish_part():
    completion_manager = CompletionManager(finish_reason="stop")
    usage_manager = UsageManager(completion=20, prompt=10, total=30)
    completion_manager.usage = usage_manager
    tool_manager = ToolManager(id="1", name="example_tool", buffer='{"key": "value"}')
    completion_manager.tool = tool_manager
    step_finish_part = completion_manager.step_finish_part()
    assert isinstance(step_finish_part, StepFinish)
    assert step_finish_part.is_continued is True
    assert step_finish_part.finish_reason == "stop"
    assert step_finish_part.usage.model_dump(by_alias=True) == {
        "promptTokens": 10,
        "completionTokens": 20,
        "totalTokens": 30,
    }


def test_completionmanager_finish_part():
    usage_manager = UsageManager(completion=20, prompt=10, total=30)
    completion_manager = CompletionManager(usage=usage_manager, finish_reason="stop")

    finish_part = completion_manager.finish_part()

    assert isinstance(finish_part, Finish)
    assert finish_part.finish_reason == "stop"
    assert (
        finish_part.data
        == r'{"finishReason":"stop","usage":{"promptTokens":10,"completionTokens":20,"totalTokens":30}}'
    )
