from typing import Any, Iterable

from pydantic import BaseModel, Field, RootModel


class ToolInvocation(BaseModel):
    state: str
    call_id: str = Field(validation_alias="toolCallId")
    name: str = Field(validation_alias="toolName")
    args: Any
    result: Any


class Message(BaseModel):
    role: str
    content: str
    tool_invocations: list[ToolInvocation] | None = Field(
        default=None, validation_alias="toolInvocations"
    )


class Messages(RootModel):
    root: list[Message]

    def to_openai(self) -> Iterable[Any]:
        new_messages = []

        for message in self.root:
            if message.tool_invocations:
                tool = message.tool_invocations[0]
                new_messages.append(
                    {
                        "role": message.role,
                        "content": message.content,
                        "tool_calls": [
                            {
                                "type": "function",
                                "id": tool.call_id,
                                "function": {
                                    "name": tool.name,
                                    "arguments": str(tool.args),
                                },
                            }
                        ],
                    }
                )
                new_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool.call_id,
                        "content": str(tool.result),
                    }
                )

            else:
                new_messages.append(
                    {
                        "role": message.role,
                        "content": message.content,
                    }
                )

        return new_messages
