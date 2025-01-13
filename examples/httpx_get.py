import httpx
from rich import print


def main() -> None:
    url = "https://developers.binance.com/docs/binance-spot-api-docs"
    resp = httpx.get(url, follow_redirects=True)
    resp.raise_for_status()

    print(resp.text)


if __name__ == "__main__":
    main()
