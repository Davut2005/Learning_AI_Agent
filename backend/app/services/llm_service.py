
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from ..config import settings

DEFAULT_MODEL = "gpt-4o-mini"


def get_llm(model: str = DEFAULT_MODEL) -> ChatOpenAI:
    """Return a LangChain ChatOpenAI instance."""
    return ChatOpenAI(
        model=model,
        api_key=settings.OPENAI_API_KEY,
        temperature=0,
    )


def generate_response(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """
    Send the prompt to OpenAI via LangChain and return the generated text.
    """
    llm = get_llm(model=model)
    msg = llm.invoke([HumanMessage(content=prompt)])
    return (msg.content or "").strip()
