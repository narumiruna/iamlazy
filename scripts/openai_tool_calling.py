import json
from typing import Literal

import httpx
from markdownify import markdownify as md
from openai import OpenAI
from openai import pydantic_function_tool
from openai.types.chat import ChatCompletion
from pydantic import BaseModel
from pydantic import Field
from rich import print


class GoogleSearch(BaseModel):
    keywords: list[str] = Field(..., description="The keywords to search for")

    def __call__(self) -> str:
        response = httpx.get(
            url="https://www.google.com/search",
            params={"q": " ".join(self.keywords)},
        )

        response.raise_for_status()
        return md(response.text, strip=["a", "img"]).strip()


class Client:
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0,
        tools: list[type[BaseModel]] | None = None,
    ) -> None:
        self.client = OpenAI()
        self.model = model
        self.temperature = temperature
        self.messages = []
        self.tools = {tool.__name__: tool for tool in tools} if tools else {}

    def send(self) -> ChatCompletion:
        kwargs = {
            "model": self.model,
            "messages": self.messages,
            "temperature": self.temperature,
        }

        if self.tools:
            kwargs["tools"] = [pydantic_function_tool(tool) for tool in self.tools.values()]

        response = self.client.chat.completions.create(**kwargs)
        response = self.handle_tool_call_response(response)
        return response

    def add(self, role: Literal["system", "user"], content: str) -> None:
        self.messages.append({"role": role, "content": content})

    def handle_tool_call_response(self, response: ChatCompletion) -> ChatCompletion:
        if not response.choices:
            return response

        choice = response.choices[0]
        if choice.finish_reason != "tool_calls":
            return response

        self.messages += [choice.message]

        for tool_call in choice.message.tool_calls:
            tool = self.tools.get(tool_call.function.name)
            if not tool:
                continue

            self.messages += [
                {
                    "role": "tool",
                    "content": tool(**json.loads(tool_call.function.arguments))(),
                    "tool_call_id": tool_call.id,
                }
            ]

        response = self.send()
        return self.handle_tool_call_response(response)


def main() -> None:
    client = Client(tools=[GoogleSearch])
    client.add("user", "台北的天氣？")
    response = client.send()
    print(response)


if __name__ == "__main__":
    main()
