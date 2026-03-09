"""
Concept extraction service: extract technical concepts from document chunks using the LLM.
"""

import json
import re
from typing import List, Union

from sqlmodel import Session, select

from app.models import Concept
from app.services.llm_service import generate_response

PROMPT_TEMPLATE = """Extract the key technical concepts from the following text.

Rules:
- Only extract important learning concepts.
- Avoid generic words like "introduction", "example", "code".
- Return at most 5 concepts.
- Return ONLY valid JSON.

Format:

{
  "concepts": [
    "concept1",
    "concept2",
    "concept3"
  ]
}

Text:
{text_chunk}
"""


def _parse_concepts_response(response: str) -> List[str]:
    """Parse LLM response into a list of concept strings. Handles markdown code blocks."""
    text = response.strip()
    # Remove optional ```json ... ``` wrapper
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1).strip()
    data = json.loads(text)
    concepts = data.get("concepts") or []
    return [c.strip() for c in concepts if isinstance(c, str) and c.strip()]


def extract_concepts_from_chunk(
    document_id: Union[int, str],
    chunk_text: str,
    db: Session,
) -> List[str]:
    """
    Extract technical concepts from chunk text via LLM, insert into concepts table,
    skip duplicates for the same document. Returns the list of extracted concept names.
    document_id can be int or str (converted to int for the DB).
    """
    doc_id = int(document_id) if isinstance(document_id, str) else document_id
    if not chunk_text or not chunk_text.strip():
        return []

    prompt = PROMPT_TEMPLATE.format(text_chunk=chunk_text.strip())
    response = generate_response(prompt)
    concepts = _parse_concepts_response(response)
    if not concepts:
        return []

    # Existing concept names for this document (case-insensitive dedup)
    existing = {
        (row[0] or "").lower()
        for row in db.exec(
            select(Concept.name).where(Concept.document_id == doc_id)
        ).all()
    }

    inserted: List[str] = []
    for name in concepts:
        if not name or len(name) > 255:
            continue
        if name.lower() in existing:
            continue
        db.add(
            Concept(
                document_id=doc_id,
                name=name[:255],
                description=None,
            )
        )
        existing.add(name.lower())
        inserted.append(name)

    db.commit()
    return inserted
