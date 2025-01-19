from __future__ import annotations

from enum import Enum

import httpx
from dotenv import find_dotenv
from dotenv import load_dotenv
from markdownify import markdownify as md
from openai import OpenAI
from pydantic import BaseModel
from pydantic import Field
from rich import print


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
    change: str
    category: Category


class Entry(BaseModel):
    date: Date
    changes: list[Change] = Field(..., description="The changes made")


class Changelog(BaseModel):
    entries: list[Entry]


def main() -> None:
    load_dotenv(find_dotenv())

    url = "https://developers.binance.com/docs/binance-spot-api-docs"
    resp = httpx.get(url)
    resp.raise_for_status()
    content = md(resp.text, strip=["a", "img"])

    client = OpenAI()
    response = client.beta.chat.completions.parse(
        messages=[{"role": "user", "content": content[:5000]}],
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
