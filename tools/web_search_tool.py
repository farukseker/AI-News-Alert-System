from pydantic import BaseModel, Field
from langchain.tools import tool
from ddgs import DDGS


class WebUrlSearchInput(BaseModel):
    query: str = Field(..., description="The URL to fetch content from")


@tool(
    description="Search the internet for up-to-date information such as news, current events, weather, or market data.",
    args_schema=WebUrlSearchInput
)
def internet_search_tool(query: str):
    """
    Use this when asked for general internet information
    that isn't in the database, such as current events, weather, or the stock market.
    """
    try:
        results = DDGS().text(query=query, max_results=3)
        return str(results)
    except Exception as e:
        return f"İnternete arama hatası alındı: {str(e)}"

__all__ = "internet_search_tool",