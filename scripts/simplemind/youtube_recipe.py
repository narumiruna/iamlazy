import simplemind as sm
from dotenv import find_dotenv
from dotenv import load_dotenv
from pydantic import BaseModel
from rich import print

from iamlazy.loaders import PipelineLoader


class Ingredient(BaseModel):
    name: str
    quantity: str
    unit: str
    preparation: str


class Step(BaseModel):
    description: str
    ingredients: list[Ingredient]


class Recipe(BaseModel):
    title: str
    ingredients: list[Ingredient]
    steps: list[Step]


def main() -> None:
    load_dotenv(find_dotenv())

    url = "https://youtu.be/esSqXd7Jxb0"
    content = PipelineLoader().load(url)

    print(content)

    prompt = f"""
    從字幕中抽取食譜訊息，不要捏造任何訊息。抽取後翻譯成台灣繁體中文。

    字幕：
    ```
    {content}
    ```
    """
    data = sm.generate_data(
        prompt,
        llm_model="gpt-4o-mini",
        llm_provider="openai",
        response_model=Recipe,
    )
    print(data)


if __name__ == "__main__":
    main()
