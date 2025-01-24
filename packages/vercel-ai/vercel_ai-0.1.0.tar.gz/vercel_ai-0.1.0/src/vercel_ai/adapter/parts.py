import json
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class PartType(StrEnum):
    TEXT = "text-delta"
    TOOL_CALL = "tool-call"
    TOOL_RESULT = "tool-result"
    STEP_START = "step-start"
    STEP_FINISH = "step-finish"
    FINISH = "finish"
    ERROR = "error"


class StreamPart(BaseModel):
    type: PartType
    code: str

    @property
    def data(self) -> str: ...

    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        return f"{self.code}:{self.data}\n".encode(encoding, errors)


class TokenUsage(BaseModel):
    prompt_tokens: int = Field(default=0, serialization_alias="promptTokens")
    completion_tokens: int = Field(default=0, serialization_alias="completionTokens")
    total_tokens: int = Field(default=0, serialization_alias="totalTokens")


class Text(StreamPart):
    text_delta: str = Field(serialization_alias="textDelta")

    type: PartType = Field(init=False, default=PartType.TEXT, exclude=True)
    code: str = Field(init=False, default="0", exclude=True)

    @property
    def data(self) -> str:
        return json.dumps(self.text_delta)


class ToolCall(StreamPart):
    id: str = Field(serialization_alias="toolCallId")
    name: str = Field(serialization_alias="toolName")
    args: dict

    type: PartType = Field(init=False, default=PartType.TOOL_CALL, exclude=True)
    code: str = Field(init=False, default="9", exclude=True)

    @property
    def data(self) -> str:
        return self.model_dump_json(by_alias=True)


class ToolResult(StreamPart):
    tool_call_id: str = Field(serialization_alias="toolCallId")
    result: Any

    type: PartType = Field(init=False, default=PartType.TOOL_RESULT, exclude=True)
    code: str = Field(init=False, default="a", exclude=True)

    @property
    def data(self) -> str:
        return self.model_dump_json(by_alias=True)


class StepStart(StreamPart):
    message_id: str = Field(serialization_alias="messageId")

    type: PartType = Field(init=False, default=PartType.STEP_START, exclude=True)
    code: str = Field(init=False, default="f", exclude=True)

    @property
    def data(self) -> str:
        return self.model_dump_json(by_alias=True)


class StepFinish(StreamPart):
    finish_reason: str = Field(serialization_alias="finishReason")
    usage: TokenUsage = TokenUsage()
    is_continued: bool = Field(serialization_alias="isContinued")

    type: PartType = Field(init=False, default=PartType.STEP_FINISH, exclude=True)
    code: str = Field(init=False, default="e", exclude=True)

    @property
    def data(self) -> str:
        return self.model_dump_json(by_alias=True)


class Finish(StreamPart):
    finish_reason: str = Field(serialization_alias="finishReason")
    usage: TokenUsage = TokenUsage()

    type: PartType = Field(init=False, default=PartType.FINISH, exclude=True)
    code: str = Field(init=False, default="d", exclude=True)

    @property
    def data(self) -> str:
        return self.model_dump_json(by_alias=True)


class Error(StreamPart):
    error: str

    type: PartType = Field(init=False, default=PartType.ERROR, exclude=True)
    code: str = Field(init=False, default="3", exclude=True)

    @property
    def data(self) -> str:
        return self.model_dump_json(by_alias=True)
