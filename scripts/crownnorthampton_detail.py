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


class Size(BaseModel):
    uk: float
    cm: float


class Product(BaseModel):
    name: str
    price: Price
    url: str
    sole_colours: list[str]
    # sizes: list[str]
    sizes: list[Size]
    width_fittings: list[str]
    descriptions: list[str] = Field(..., description="The description of the product in Traditional Chinese.")
    materials: list[str]


@openai.call("gpt-4o-mini", response_model=Product)
def extract_product(content: str) -> Product:
    prompt = f"""
    Extract product details from the given passage.
    Do not fabricate any information.

    Passage:
    {content}
    """
    return prompt


def main() -> None:
    load_dotenv(find_dotenv())

    url = "https://crownnorthampton.com/collections/bestsellers/products/overstone-derby-all-white-calf-leather"

    resp = httpx.get(url, follow_redirects=True)
    resp.raise_for_status()

    content = md(resp.text, strip=["img"])

    products = extract_product(content)
    for product in products:
        print(product)


if __name__ == "__main__":
    main()
