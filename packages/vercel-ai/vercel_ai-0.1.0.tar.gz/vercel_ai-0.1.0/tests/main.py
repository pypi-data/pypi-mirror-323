from typing import Iterable, Any
from fastapi import FastAPI
from openai import AsyncAzureOpenAI
from vercel_ai.fastapi import StreamText, RequestData

app = FastAPI()

client = AsyncAzureOpenAI(
    azure_endpoint="https://chatnormativa.openai.azure.com/",
    api_key="4b5efbf0a2a941a2aa5225ab7fca75bf",
    api_version="2023-07-01-preview",
)


tools: Iterable[Any] = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current temperature for provided coordinates in celsius.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                },
                "required": ["location"],
            },
        },
    }
]


async def get_weather(location: str):
    return {"temperature": 25, "location": location}


tool_map = {"get_weather": get_weather}


@app.post("/chat")
async def chat(input: RequestData):
    response = await client.chat.completions.create(
        model="gpt-4-turbo",
        messages=input.messages.to_openai(),
        tools=tools,
        stream=True,
    )

    return StreamText(response, tool_map=tool_map)
