import json
import random

import openai
from dotenv import find_dotenv
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from pydantic import Field
from rich import print


class GetWeather(BaseModel):
    """一個用來取的天氣資訊的工具"""

    location: str = Field(..., description="想要查詢天氣的地點")

    def __call__(self) -> str:
        weather = random.choice(["晴天", "陰天", "雨天"])
        temperature = random.randint(10, 30)
        return f"天氣：{weather}\n氣溫：{temperature}度"


def main() -> None:
    load_dotenv(find_dotenv())

    model = "gpt-4o-mini"
    temperature = 0
    messages = [{"role": "user", "content": "台北的天氣如何？"}]

    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=[openai.pydantic_function_tool(GetWeather)],
        temperature=temperature,
    )

    messages += [response.choices[0].message]

    for tool_call in response.choices[0].message.tool_calls:
        if tool_call.function.name == "GetWeather":
            messages += [
                {
                    "role": "tool",
                    "content": GetWeather(**json.loads(tool_call.function.arguments))(),
                    "tool_call_id": tool_call.id,
                }
            ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
