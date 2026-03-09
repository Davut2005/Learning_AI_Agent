"""
Concept extraction service: extract technical concepts from document chunks using the LLM.
Uses LangChain + OpenAI with robust JSON parsing and duplicate handling.
"""

import json
import logging
import re
from typing import List

from sqlmodel import Session, select

from app.database import engine
from app.models import Concept
from app.services.llm_service import generate_response

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """You are a technical knowledge extractor.

Your task is to identify the most important learning concepts from a technical text.

Rules:
- Extract only meaningful technical concepts.
- Avoid generic words such as: example, code, introduction, section, snippet, tutorial.
- Concepts must be between 1 and 4 words.
- Prefer specific technologies, APIs, algorithms, programming ideas, or software components.
- Maximum 5 concepts.
- Do NOT explain anything.

Return ONLY valid JSON.

JSON format:
{
 "concepts": ["concept1","concept2","concept3"]
}

Text:
{chunk_text}
"""


def _clean_llm_json_output(response: str) -> str:
    """
    Clean the LLM output before parsing JSON:
    - Remove ```json and ``` if present
    - Remove leading or trailing text outside the JSON
    - Trim whitespace
    """
    text = response.strip()
    # Remove markdown code block
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```\s*$", "", text)
    text = text.strip()
    # Try to find JSON object (first { to last })
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end >= start:
        text = text[start : end + 1]
    return text.strip()


def _parse_concepts_response(response: str) -> List[str]:
    """
    Parse LLM response into a list of concept strings.
    Returns empty list on any parse error; logs failure for debugging.
    """
    cleaned = _clean_llm_json_output(response)
    if not cleaned:
        logger.warning("Concept extraction: cleaned LLM output is empty")
        return []
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.warning(
            "Concept extraction: invalid JSON from model. error=%s raw=%s",
            e,
            response[:500] if response else "",
        )
        return []
    concepts = data.get("concepts")
    if not isinstance(concepts, list):
        logger.warning("Concept extraction: 'concepts' is not a list. keys=%s", data.keys() if isinstance(data, dict) else type(data))
        return []
    return [c.strip() for c in concepts if isinstance(c, str) and c.strip()]


def extract_concepts_from_chunk(document_id: str, chunk_text: str) -> List[str]:
    """
    Extract technical concepts from chunk text via LLM (LangChain + OpenAI), insert into concepts table,
    skip duplicates for the same document. Returns the list of inserted concept names.
    """
    if not chunk_text or not chunk_text.strip():
        return []

    try:
        doc_id = int(document_id)
    except (ValueError, TypeError):
        logger.warning("Concept extraction: document_id must be numeric, got %r", document_id)
        return []

    prompt = PROMPT_TEMPLATE.format(chunk_text=chunk_text.strip())
    response = generate_response(prompt)
    concepts = _parse_concepts_response(response)
    if not concepts:
        return []

    inserted: List[str] = []
    with Session(engine) as db:
        for name in concepts:
            if not name or len(name) > 255:
                continue
            name_trimmed = name[:255]
            # Avoid duplicates: insert only if not already present for this document
            existing = db.exec(
                select(Concept.id).where(
                    Concept.document_id == doc_id,
                    Concept.name == name_trimmed,
                )
            ).first()
            if existing is not None:
                continue
            db.add(
                Concept(
                    document_id=doc_id,
                    name=name_trimmed,
                    description=None,
                )
            )
            inserted.append(name_trimmed)
        db.commit()

    return inserted
