from enum import Enum
from typing import Final

import httpx
from dotenv import find_dotenv
from dotenv import load_dotenv
from markdownify import markdownify as md
from mirascope.core import openai
from pydantic import BaseModel
from pydantic import Field

MODEL: Final[str] = "gpt-4o"
TEMPERATURE: Final[float] = 0.0


class Step(BaseModel):
    explanation: str
    output: str

    def __str__(self) -> str:
        return f"🤔 {self.explanation}\n   ➡️ {self.output}"


class Reasoning(BaseModel):
    steps: list[Step]
    final_answer: str


class CausalRelationship(BaseModel):
    cause: str
    effect: str
    # reasoning: Reasoning

    def __str__(self) -> str:
        return f"{self.cause} ➡️ {self.effect}"
        # steps = "\n".join(str(step) for step in self.reasoning.steps)
        # return f"{self.cause} ➡️ {self.effect}\n" f"推理過程：\n{steps}"


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class SentimentAnalysis(BaseModel):
    sentiment: Sentiment
    # reasoning: Reasoning
    target_market: str
    score: float = Field(
        ...,
        description="The sentiment score, between -1 and 1. A higher score indicates a more positive sentiment.",
    )

    def __str__(self) -> str:
        return f"{self.sentiment.value} ({self.score}), target: {self.target_market}"
        # steps = "\n".join(str(step) for step in self.reasoning.steps)
        # return f"{self.sentiment.value} ({self.score})\n" f"推理過程：\n{steps}"


class Analysis(BaseModel):
    sentiment: SentimentAnalysis
    summary: str
    causal_relations: list[CausalRelationship]  # Added new field
    insights: list[str]
    hashtags: list[str]
    affected_markets: list[str]

    def __str__(self) -> str:
        relations = ""
        for relation in self.causal_relations:
            relations += str(relation) + "\n"
        return (
            "📊 分析報告\n"
            f"💭 情感分析：{self.sentiment}\n"
            f"📝 摘要：{self.summary}\n"
            f"🔗 因果關係：{relations}\n"
            f"💡 重要見解：\n" + "\n".join(f"   • {insight}" for insight in self.insights) + "\n"
            "🏷️ 標籤：" + " ".join(self.hashtags) + "\n"
            "💱 相關市場：" + "、".join(self.affected_markets)
        )


class OverallAnalysis(BaseModel):
    sentiment: SentimentAnalysis
    summary: str
    insights: list[str]
    hashtags: list[str]
    affected_markets: list[str]

    def __str__(self) -> str:
        return (
            "\n🔍 整體分析報告\n"
            f"💭 整體情感：{self.sentiment}\n"
            f"📋 綜合摘要：{self.summary}\n"
            f"💎 核心見解：\n" + "\n".join(f"   • {insight}" for insight in self.insights) + "\n"
            "🔖 相關標籤：" + " ".join(self.hashtags) + "\n"
            "💰 相關市場：" + "、".join(self.affected_markets)
        )


@openai.call(MODEL, call_params={"temperature": TEMPERATURE}, response_model=SentimentAnalysis)
def analyze_sentiment(content: str) -> str:
    prompt = f"""
    情感分析以下加密貨幣新聞文章：
    請用繁體中文回答。請基於文章內容分析，不要添加臆測資訊。
    列出計算出 score 的過程。

    文章內容：
    {content}
    """.strip()

    return prompt


@openai.call(MODEL, call_params={"temperature": TEMPERATURE}, response_model=Analysis)
def analyze_text(content: str) -> str:
    prompt = f"""
    分析以下加密貨幣新聞文章，並提供詳細分析：

    1. 情感分析：評估文章整體論調對加密貨幣市場的影響
    2. 摘要：提供100字以內的核心重點
    3. 重要見解：列出3-5個關鍵洞察
    4. 標籤：加入5個相關的主題標籤
    5. 相關市場：列出可能受影響的加密貨幣、股票或其他金融市場
    6. 因果關係：列出多個可能的因果關係

    請用繁體中文回答。請基於文章內容分析，不要添加臆測資訊。

    文章內容：
    {content}
    """.strip()

    return prompt


@openai.call(MODEL, call_params={"temperature": TEMPERATURE}, response_model=OverallAnalysis)
def overall_analysis(contents: list[str]) -> str:
    prompt = """
    綜合分析以下多篇新聞的結果，提供整體市場觀察：

    1. 整體情感：評估整體市場氛圍
    2. 綜合摘要：150字內總結主要市場動向
    3. 核心見解：提供3-5個綜合性觀察
    4. 相關標籤：歸納5個重要主題標籤
    5. 相關市場：列出受影響程度最大的市場

    請用繁體中文回答。請基於提供的分析內容，不要添加臆測資訊。
    如果某些新聞影響較小或不相關，請說明原因。

    分析結果：
    """.strip()

    for i, content in enumerate(contents, 1):
        prompt += f"\n\n第 {i} 篇分析：\n{content}"
    return prompt


def trim_and_filter_lines(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            lines += [stripped]
    return "\n".join(lines)


def load_html(url: str) -> str:
    response = httpx.get(url, follow_redirects=True)
    response.raise_for_status()

    content = md(response.text, strip=["a", "img"])
    return trim_and_filter_lines(content)


def main() -> None:
    load_dotenv(find_dotenv())

    urls = [
        "https://www.coindesk.com/markets/2025/02/04/bitcoin-down-2-5-as-china-slaps-retaliatory-tariffs-on-u-s-coal",
        # "https://www.coindesk.com/sponsored-content/golfin-connecting-games-and-real-life-golf-with-web3-technology-ceo-komatsu-talks-about-the-challenge-of-a-new-ecosystem",
        # "https://www.coindesk.com/policy/2025/02/03/u-s-prosecutors-charge-canadian-man-with-usd65m-hacks-of-indexed-finance-kyberswap",
        # "https://www.coindesk.com/opinion/2025/02/03/10-commandments-for-federal-securities-laws",
        # "https://www.coindesk.com/markets/2025/02/03/microstrategy-pauses-weekly-bitcoin-purchases-ahead-of-earnings",
    ]

    results = []
    for url in urls:
        content = load_html(url)
        # response = analyze_text(content)
        # response = analyze_sentiment(content)
        response = analyze_text(content)
        results.append(response)

    # overall_response = overall_analysis([str(result) for result in results])

    for result, url in zip(results, urls, strict=True):
        print("=" * 50)
        print(url)
        print(result)

    # print("=" * 50)
    # print(overall_response)


if __name__ == "__main__":
    main()
