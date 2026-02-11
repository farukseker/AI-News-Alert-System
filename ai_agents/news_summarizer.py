from typing import List

import re

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from guardrails import Guard
from pydantic import BaseModel, Field

from config import get_settings

settings = get_settings()

TEMPLATE_DIR = settings.BASE_DIR / "prompts_templates"

with open(TEMPLATE_DIR / "news_summarizer_prompt.md", "r", encoding="utf-8") as f:
    news_summarizer_prompt = f.read().strip()

with open(TEMPLATE_DIR / "news_summarizer_request.md", "r", encoding="utf-8") as f:
    news_summarizer_request = f.read().strip()


class Output(BaseModel):
    piantik: bool
    confidence: float = Field(ge=0.0, le=1.0)
    summary: str
    events: List[str]


guard = Guard.for_pydantic(Output)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", news_summarizer_prompt),
        ("human", news_summarizer_request),
    ]
)

llm = ChatOpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url=settings.OPENROUTER_BASE_URL,
    model=settings.SUMMARIZER_MODEL,
    temperature=0,
    default_headers={
        "HTTP-Referer": "https://farukseker.com.tr",
        "X-Title": "Faruk AIo",
    },
    max_retries=3,
)

chain = prompt | llm


def analyze_news(text: str, now: str, urls: list[str] | str) -> Output:
    """
    Main entry point.
    Invokes the prompt chain directly (no agent) and validates output via Guardrails.
    """
    print("[INFO] Starting news analysis")

    raw_response = chain.invoke(
        {
            "text": text,
            "now": now,
            "urls": "\n".join(urls) if isinstance(urls, list) else urls,
        }
    )

    print("[DEBUG] Raw response type:", type(raw_response))

    # Extract string content from the AIMessage object returned by LangChain
    if hasattr(raw_response, "content"):
        content = raw_response.content
    elif isinstance(raw_response, dict):
        content = raw_response.get("output") or raw_response.get("content") or str(raw_response)
    else:
        content = str(raw_response)

    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
    if fence_match:
        content = fence_match.group(1)

    print("[DEBUG] Extracted content:", content)

    validated_output = Output.model_validate_json(content)

    print("[INFO] Analysis complete")
    return validated_output

__all__ = "analyze_news",