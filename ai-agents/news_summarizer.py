from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from guardrails import Guard
from pydantic import BaseModel

class Output(BaseModel):
    result: str
    confidence: float

guard = Guard.for_pydantic(Output)

