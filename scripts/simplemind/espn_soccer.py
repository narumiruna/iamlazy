import httpx
import simplemind as sm
from dotenv import find_dotenv
from dotenv import load_dotenv
from markdownify import markdownify as md
from pydantic import BaseModel
from rich import print


class Commentary(BaseModel):
    time: str
    text: str


class Match(BaseModel):
    commentaries: list[Commentary]


def main() -> None:
    load_dotenv(find_dotenv())
    url = "https://espn.com/soccer/commentary/_/gameId/704489"

    resp = httpx.get(url, follow_redirects=True)
    resp.raise_for_status()

    content = md(resp.text, strip=["a", "img"])
    print(content)

    prompt = f"""
    Extract commentaries from the given passage.
    Do not fabricate any information.

    Passage:
    ```
    {content}
    ```
    """
    data = sm.generate_data(
        prompt,
        llm_model="gpt-4o-mini",
        llm_provider="openai",
        response_model=Match,
    )
    print(data)


if __name__ == "__main__":
    main()
