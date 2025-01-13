from typing import Annotated

import httpx
import simplemind as sm
from markdownify import markdownify as md
from pydantic import Field
from rich import print


def google_search(
    query: Annotated[str, Field(description="The query to search for")],
) -> str:
    """A tool that searches Google for the given query."""
    response = httpx.get(
        url="https://www.google.com/search",
        params={"q": query},
    )
    response.raise_for_status()
    return md(response.text, strip=["a", "img"]).strip()


def main() -> None:
    conversation = sm.create_conversation(
        llm_model="gpt-4o-mini",
        llm_provider="openai",
    )
    conversation.add_message("user", "台北的天氣？")

    response = conversation.send(tools=[google_search])
    print(response.text)


if __name__ == "__main__":
    main()
