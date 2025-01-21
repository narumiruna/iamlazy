from typing import Literal

import httpx
from dotenv import find_dotenv
from dotenv import load_dotenv
from markdownify import markdownify as md
from mirascope.core import openai
from pydantic import BaseModel
from pydantic import Field
from rich import print


class Price(BaseModel):
    value: float
    currency: str = Field(..., description="The currency of the price in ISO 4217 format.")


class PriceRange(BaseModel):
    min: Price
    max: Price


class Budget(BaseModel):
    # price_range: PriceRange
    price_range: str
    dinner_or_lunch: Literal["dinner", "lunch"]


class Restaurant(BaseModel):
    name: str
    description: str
    url: str
    dinner_budget: Budget
    lunch_budget: Budget
    rating: float
    rating_count: int
    location: str


@openai.call("gpt-4o-mini", response_model=list[Restaurant])
def extract_restaurants(content: str) -> list[Restaurant]:
    prompt = f"""
    Extract restaurants from the given passage.
    Do not fabricate any information.

    Passage:
    {content}
    """
    return prompt


def main() -> None:
    load_dotenv(find_dotenv())
    url = "https://tabelog.com/rstLst/tonkatsu/?SrtT=rt&Srt=D&sort_mode=1"

    resp = httpx.get(url, follow_redirects=True)
    resp.raise_for_status()

    content = md(resp.text, strip=["img"])
    print(content)

    restaurants = extract_restaurants(content)
    for restaurant in restaurants:
        print(restaurant)


if __name__ == "__main__":
    main()
