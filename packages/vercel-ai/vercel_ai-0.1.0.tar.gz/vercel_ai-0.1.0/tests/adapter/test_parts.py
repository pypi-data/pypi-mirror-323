import json

from vercel_ai.adapter.parts import (
    PartType,
    TokenUsage,
    Text,
    ToolCall,
    ToolResult,
    StepStart,
    StepFinish,
    Finish,
    Error,
)


def test_token_usage():
    usage = TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30)

    assert usage.prompt_tokens == 10
    assert usage.completion_tokens == 20
    assert usage.total_tokens == 30

    assert usage.model_dump(by_alias=True) == {
        "promptTokens": 10,
        "completionTokens": 20,
        "totalTokens": 30,
    }


def test_text():
    text_part = Text(text_delta="Hello, world!")

    assert text_part.type == PartType.TEXT
    assert text_part.code == "0"
    assert text_part.data == json.dumps("Hello, world!")
    assert text_part.encode() == b'0:"Hello, world!"\n'


def test_tool_call():
    tool_call_part = ToolCall(id="123", name="test_tool", args={"key": "value"})

    assert tool_call_part.type == PartType.TOOL_CALL
    assert tool_call_part.code == "9"
    assert (
        tool_call_part.data
        == r'{"toolCallId":"123","toolName":"test_tool","args":{"key":"value"}}'
    )
    assert (
        tool_call_part.encode()
        == b'9:{"toolCallId":"123","toolName":"test_tool","args":{"key":"value"}}\n'
    )


def test_tool_result():
    tool_result_part = ToolResult(tool_call_id="123", result="Success")
    assert tool_result_part.type == PartType.TOOL_RESULT
    assert tool_result_part.code == "a"
    assert tool_result_part.data == r'{"toolCallId":"123","result":"Success"}'
    assert tool_result_part.encode() == b'a:{"toolCallId":"123","result":"Success"}\n'


def test_step_start():
    step_start_part = StepStart(message_id="456")
    assert step_start_part.type == PartType.STEP_START
    assert step_start_part.code == "f"
    assert step_start_part.data == r'{"messageId":"456"}'
    assert step_start_part.encode() == b'f:{"messageId":"456"}\n'


def test_step_finish():
    step_finish_part = StepFinish(
        finish_reason="stop",
        usage=TokenUsage(prompt_tokens=10, completion_tokens=20),
        is_continued=False,
    )
    assert step_finish_part.type == PartType.STEP_FINISH
    assert step_finish_part.code == "e"
    assert (
        step_finish_part.data
        == r'{"finishReason":"stop","usage":{"promptTokens":10,"completionTokens":20,"totalTokens":0},"isContinued":false}'
    )
    assert (
        step_finish_part.encode()
        == b'e:{"finishReason":"stop","usage":{"promptTokens":10,"completionTokens":20,"totalTokens":0},"isContinued":false}\n'
    )


def test_finish():
    finish_part = Finish(
        finish_reason="stop", usage=TokenUsage(prompt_tokens=10, completion_tokens=20)
    )

    assert finish_part.type == PartType.FINISH
    assert finish_part.code == "d"

    assert (
        finish_part.data
        == r'{"finishReason":"stop","usage":{"promptTokens":10,"completionTokens":20,"totalTokens":0}}'
    )
    assert (
        finish_part.encode()
        == b'd:{"finishReason":"stop","usage":{"promptTokens":10,"completionTokens":20,"totalTokens":0}}\n'
    )


def test_error():
    error_part = Error(error="An error occurred")
    assert error_part.type == PartType.ERROR
    assert error_part.code == "3"
    assert error_part.data == '{"error":"An error occurred"}'
    assert error_part.encode() == b'3:{"error":"An error occurred"}\n'
