import simplemind as sm
from dotenv import find_dotenv
from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic import Field
from rich import print

from iamlazy.loaders import PipelineLoader


class Exercise(BaseModel):
    name: str
    tier: str
    reason: str


class Exercises(BaseModel):
    exercises: list[Exercise]
    summary: str


def main() -> None:
    load_dotenv(find_dotenv())

    url = "https://youtu.be/fGm-ef-4PVk"
    content = PipelineLoader().load(url)

    print(content)

    prompt = f"""
    從字幕中抽取資訊，不要捏造任何資訊。抽取後翻譯成台灣繁體中文。

    字幕：
    ```
    {content}
    ```
    """
    data = sm.generate_data(
        prompt,
        llm_model="gpt-4o-mini",
        llm_provider="openai",
        response_model=Exercises,
    )
    print(data)


if __name__ == "__main__":
    main()
