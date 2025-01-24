from uuid import uuid4
from typing import AsyncIterable, Awaitable, Callable, Optional

from openai.types.chat import ChatCompletionChunk

from ..adapter.manager import CompletionManager
from ..adapter.parts import StreamPart


async def stream_completion(
    completion: AsyncIterable[ChatCompletionChunk],
    id: str = uuid4().hex,
    tool_map: Optional[dict[str, Callable[..., Awaitable]]] = None,
) -> AsyncIterable[StreamPart]:
    m = CompletionManager()

    yield m.step_start_part(id)

    async for chunk in completion:
        if choices := chunk.choices:
            delta = choices[0].delta
            reason = choices[0].finish_reason

            if delta.content:
                yield m.text_part(delta.content)

            if delta.tool_calls:
                call = delta.tool_calls[0]
                if call.id:
                    m.tool.id = call.id
                if func := call.function:
                    if func.name:
                        m.tool.name = func.name
                    if func.arguments:
                        m.tool.buffer += func.arguments

            if usage := chunk.usage:
                m.usage.completion += usage.completion_tokens
                m.usage.prompt += usage.prompt_tokens
                m.usage.total += usage.total_tokens

            if reason:
                m.finish_reason = reason

    if m.tool.used:
        yield m.tool.call_part()

        assert tool_map is not None
        result = await tool_map[m.tool.name](**m.tool.parsed_buffer)

        yield m.tool.result_part(result)

    yield m.step_finish_part()
    yield m.finish_part()
