"""
Embedding service using LangChain + OpenAI embeddings.
"""

from typing import List

from langchain_openai import OpenAIEmbeddings

from core.config import settings

DEFAULT_MODEL = "text-embedding-3-small"


def get_embeddings(model: str = DEFAULT_MODEL) -> OpenAIEmbeddings:
    """Return a LangChain OpenAIEmbeddings instance."""
    return OpenAIEmbeddings(
        model=model,
        api_key=settings.OPENAI_API_KEY,
    )


def create_embedding(text: str, model: str = DEFAULT_MODEL) -> List[float]:
    """
    Create an embedding vector for the given text using OpenAI.
    Returns a list of floats.
    """
    embeddings = get_embeddings(model=model)
    return embeddings.embed_query(text)
