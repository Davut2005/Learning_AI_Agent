"""
Question generation service: generate quiz questions for concepts using the LLM (LangChain + OpenAI).
"""

import json
import logging
import re
from typing import Any, List

from sqlmodel import Session, select

from app.database import engine
from app.models import Concept, Question
from app.services.llm_service import generate_response

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """You are an AI that generates quiz questions for learning.

Your task is to generate quiz questions about a specific technical concept.

Concept:
{concept}

Rules:
- Questions must test understanding of the concept.
- Avoid generic questions.
- Prefer conceptual or practical understanding.
- Generate exactly 3 questions.
- Include the correct answer.
- Do NOT explain anything.

Return ONLY valid JSON.

Format:

{{
 "questions":[
  {{
   "question":"...",
   "answer":"...",
   "difficulty":"easy"
  }},
  {{
   "question":"...",
   "answer":"...",
   "difficulty":"medium"
  }},
  {{
   "question":"...",
   "answer":"...",
   "difficulty":"hard"
  }}
 ]
}}
"""


def _clean_llm_json_output(response: str) -> str:
    """
    Clean the LLM output before parsing JSON:
    - Remove ```json and ``` markers
    - Remove any extra text outside JSON
    """
    text = response.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```\s*$", "", text)
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end >= start:
        text = text[start : end + 1]
    return text.strip()


def _parse_questions_response(response: str) -> List[dict[str, Any]]:
    """
    Parse LLM response into a list of question dicts (question, answer, difficulty).
    Returns empty list on parse error; logs failure for debugging.
    """
    cleaned = _clean_llm_json_output(response)
    if not cleaned:
        logger.warning("Question generation: cleaned LLM output is empty")
        return []
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.warning(
            "Question generation: invalid JSON from model. error=%s raw=%s",
            e,
            response[:500] if response else "",
        )
        return []
    questions = data.get("questions")
    if not isinstance(questions, list):
        logger.warning("Question generation: 'questions' is not a list")
        return []
    result = []
    for q in questions:
        if not isinstance(q, dict):
            continue
        question = (q.get("question") or "").strip()
        answer = (q.get("answer") or "").strip()
        difficulty = (q.get("difficulty") or "medium").strip().lower()
        if question and answer:
            result.append({"question": question, "answer": answer, "difficulty": difficulty})
    return result


def generate_questions_for_concept(document_id: str, concept: str) -> List[dict]:
    """
    Generate quiz questions for a concept via LLM, insert into questions table,
    skip duplicates for the same concept. Returns the list of generated question dicts.
    """
    if not concept or not concept.strip():
        return []

    try:
        doc_id = int(document_id)
    except (ValueError, TypeError):
        logger.warning("Question generation: document_id must be numeric, got %r", document_id)
        return []

    # Resolve concept to concept_id (existing concepts table)
    with Session(engine) as db:
        concept_row = db.exec(
            select(Concept).where(
                Concept.document_id == doc_id,
                Concept.name == concept.strip(),
            )
        ).first()
        if not concept_row:
            logger.warning("Question generation: concept %r not found for document_id=%s", concept, doc_id)
            return []

        concept_id = concept_row.id
        prompt = PROMPT_TEMPLATE.format(concept=concept.strip())
        response = generate_response(prompt)
        questions_data = _parse_questions_response(response)
        if not questions_data:
            return []

        # Existing question texts for this concept (avoid duplicates)
        existing_texts = {
            (row[0] or "").strip()
            for row in db.exec(
                select(Question.question_text).where(Question.concept_id == concept_id)
            ).all()
        }

        inserted: List[dict] = []
        for q in questions_data:
            question_text = q["question"]
            if question_text in existing_texts:
                continue
            db.add(
                Question(
                    concept_id=concept_id,
                    question_text=question_text,
                    question_type="quiz",
                    options={"difficulty": q["difficulty"]},
                    correct_answer=q["answer"],
                )
            )
            existing_texts.add(question_text)
            inserted.append(
                {
                    "question": question_text,
                    "answer": q["answer"],
                    "difficulty": q["difficulty"],
                }
            )
        db.commit()

    return inserted
