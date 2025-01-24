from typing import Any

from vercel_ai.adapter.messages import (
    ToolInvocation,
    Message,
    Messages,
)


# Test ToolInvocation model
def test_tool_invocation():
    tool_invocation = ToolInvocation(
        state="completed",
        toolCallId="12345",  # type: ignore
        toolName="example_tool",  # type: ignore
        args={"key": "value"},
        result="success",
    )
    assert tool_invocation.state == "completed"
    assert tool_invocation.call_id == "12345"
    assert tool_invocation.name == "example_tool"
    assert tool_invocation.args == {"key": "value"}
    assert tool_invocation.result == "success"


# Test Message model
def test_message():
    message = Message(
        role="user",
        content="Hello, world!",
        tool_invocations=[
            ToolInvocation(
                state="completed",
                toolCallId="12345",  # type: ignore
                toolName="example_tool",  # type: ignore
                args={"key": "value"},
                result="success",
            )
        ],
    )
    assert message.role == "user"
    assert message.content == "Hello, world!"
    assert message.tool_invocations is not None
    assert len(message.tool_invocations) == 1
    assert message.tool_invocations[0].name == "example_tool"


def test_message_without_tool_invocations():
    message = Message(role="assistant", content="Goodbye, world!")
    assert message.role == "assistant"
    assert message.content == "Goodbye, world!"
    assert message.tool_invocations is None


# Test Messages model and to_openai method
def test_messages_to_openai():
    messages = Messages(
        root=[
            Message(
                role="user",
                content="Hello, world!",
                tool_invocations=[
                    ToolInvocation(
                        state="completed",
                        toolCallId="12345",  # type: ignore
                        toolName="example_tool",  # type: ignore
                        args={"key": "value"},
                        result="success",
                    )
                ],
            ),
            Message(role="assistant", content="Goodbye, world!"),
        ]
    )
    openai_format = list(messages.to_openai())
    expected_output: list[dict[str, Any]] = [
        {
            "role": "user",
            "content": "Hello, world!",
            "tool_calls": [
                {
                    "type": "function",
                    "id": "12345",
                    "function": {
                        "name": "example_tool",
                        "arguments": "{'key': 'value'}",
                    },
                }
            ],
        },
        {
            "role": "tool",
            "tool_call_id": "12345",
            "content": "success",
        },
        {
            "role": "assistant",
            "content": "Goodbye, world!",
        },
    ]
    assert openai_format == expected_output


def test_messages_empty():
    messages = Messages(root=[])
    openai_format = list(messages.to_openai())
    assert openai_format == []
