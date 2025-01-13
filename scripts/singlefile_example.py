import subprocess
from pathlib import Path

from rich import print


def main() -> None:
    url = "https://docs.cdp.coinbase.com/exchange/docs/changelog"
    filename = "coinbase.html"
    browser_load_max_time = 10_000  # 10 seconds
    subprocess.run(
        [
            "single-file",
            f"--browser-load-max-time={browser_load_max_time}",
            "--block-images=true",
            "--filename-conflict-action",
            "overwrite",
            url,
            filename,
        ]
    )

    with Path(filename).open() as fp:
        print(fp.read())


if __name__ == "__main__":
    main()
