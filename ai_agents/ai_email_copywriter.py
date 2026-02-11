from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

import json

from config import get_settings

settings = get_settings()

TEMPLATE_DIR = settings.BASE_DIR / "prompts_templates"


llm = ChatOpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url=settings.OPENROUTER_BASE_URL,
    model='openai/gpt-5-mini',
    temperature=0,
    default_headers={
        "HTTP-Referer": "https://farukseker.com.tr",
        "X-Title": "Faruk AIo",
    },
    max_retries=3,
)


def _load_email_prompt() -> ChatPromptTemplate:
    with open(TEMPLATE_DIR / "ai_email_copywriter_prompt.md", "r", encoding="utf-8") as f:
        template = f.read().strip()
    return ChatPromptTemplate.from_template(template)

email_prompt = _load_email_prompt()


email_chain = email_prompt | llm | StrOutputParser()



def generate_email_html(extracted_data: dict | list) -> str:
    """
    Takes the extracted news data dict (e.g. r.model_dump()) and returns
    a complete HTML email string ready to store or send.
    """
    html: str = email_chain.invoke(
        {"extracted_json": json.dumps(extracted_data, ensure_ascii=False, indent=2)}
    )
    return html.strip()

