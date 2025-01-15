from __future__ import annotations

from enum import Enum

from dotenv import find_dotenv
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from pydantic import Field
from rich import print

from iamlazy.loaders import PipelineLoader


class Category(str, Enum):
    BREAKING_CHANGES = "breaking changes"
    NEW_FEATURES = "new features"
    DEPRECATIONS = "deprecations"
    BUG_FIXES = "bug fixes"
    PERFORMANCE_IMPROVEMENTS = "performance improvements"
    SECURITY_UPDATES = "security updates"


class Date(BaseModel):
    year: int
    month: int
    day: int


class Change(BaseModel):
    date: Date
    content: str = Field(..., description="The content of the change")
    category: Category


class Changelog(BaseModel):
    changes: list[Change]


def main() -> None:
    load_dotenv(find_dotenv())

    url = "https://developers.binance.com/docs/binance-spot-api-docs"
    text = PipelineLoader().load(url)
    print("Length of text:", len(text))

    client = OpenAI()
    response = client.beta.chat.completions.parse(
        messages=[{"role": "user", "content": text[:5000]}],
        model="gpt-4o-mini",
        temperature=0,
        response_format=Changelog,
    )

    if not response.choices:
        print("No response")
        return

    parsed = response.choices[0].message.parsed
    if not parsed:
        print("No parsed")
        return

    print(parsed)


if __name__ == "__main__":
    main()
