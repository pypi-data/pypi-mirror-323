from typing import Any, Callable

from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from ..providers.openai import stream_completion
from ..adapter.messages import Messages

__all__ = ["StreamText", "RequestData"]


class RequestData(BaseModel):
    id: str
    messages: Messages


class StreamText(StreamingResponse):
    def __init__(
        self,
        completion: Any,
        tool_map: Any | None = None,
        provider_func: Callable[..., Any] = stream_completion,
        **kwargs: Any,
    ) -> None:
        content = provider_func(completion=completion, tool_map=tool_map)
        super().__init__(content, media_type="text/event-stream", **kwargs)
