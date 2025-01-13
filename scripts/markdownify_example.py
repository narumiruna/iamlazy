import httpx
from markdownify import markdownify as md
from rich import print


def main() -> None:
    url = "https://www.google.com"

    resp = httpx.get(url)
    resp.raise_for_status()

    markdown = md(resp.text, strip=["a", "img"])
    print(markdown)


if __name__ == "__main__":
    main()
