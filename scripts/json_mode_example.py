from dotenv import find_dotenv
from dotenv import load_dotenv
from openai import OpenAI
from rich import print


def main() -> None:
    load_dotenv(find_dotenv())

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": 'Extract dates from message. JSON: {"dates": [{"year": int, "month": int, "day": int}]}',
            },
            {
                "role": "user",
                "content": "今天是2025年1月20日",
            },
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
