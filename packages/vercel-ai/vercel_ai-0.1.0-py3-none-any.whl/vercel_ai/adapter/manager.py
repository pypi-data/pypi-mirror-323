import json

from pydantic import Field
from pydantic.dataclasses import dataclass

from . import parts


@dataclass
class ToolManager:
    id: str = ""
    name: str = ""
    buffer: str = ""

    @property
    def used(self) -> bool:
        return bool(self.id and self.name and self.buffer)

    @property
    def parsed_buffer(self) -> dict:
        return json.loads(self.buffer)

    def call_part(self) -> parts.ToolCall:
        return parts.ToolCall(id=self.id, name=self.name, args=self.parsed_buffer)

    def result_part(self, result: dict) -> parts.ToolResult:
        return parts.ToolResult(tool_call_id=self.id, result=result)


@dataclass
class UsageManager:
    completion: int = 0
    prompt: int = 0
    total: int = 0

    def as_dict(self) -> dict:
        return {
            "completionTokens": self.completion,
            "promptTokens": self.prompt,
            "totalTokens": self.total,
        }

    def as_part(self) -> parts.TokenUsage:
        return parts.TokenUsage(
            prompt_tokens=self.prompt,
            completion_tokens=self.completion,
            total_tokens=self.total,
        )


@dataclass
class CompletionManager:
    buffer: str = ""
    finish_reason: str = ""
    tool: ToolManager = Field(default_factory=ToolManager)
    usage: UsageManager = Field(default_factory=UsageManager)

    def text_part(self, text_delta: str) -> parts.Text:
        self.buffer += text_delta
        return parts.Text(text_delta=text_delta)

    def step_start_part(self, id: str) -> parts.StepStart:
        return parts.StepStart(message_id=id)

    def step_finish_part(self) -> parts.StepFinish:
        return parts.StepFinish(
            is_continued=self.tool.used,
            finish_reason=self.finish_reason,
            usage=self.usage.as_part(),
        )

    def finish_part(self) -> parts.Finish:
        return parts.Finish(
            finish_reason=self.finish_reason,
            usage=self.usage.as_part(),
        )
