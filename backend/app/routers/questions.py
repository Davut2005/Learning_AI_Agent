"""List questions for quiz (by user or document)."""

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.database import get_session
from app.models import Concept, Document, Question
from app.schemas.question import QuestionOut

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("", response_model=list[QuestionOut])
def list_questions(
    user_id: int = Query(..., description="Filter by document owner"),
    document_id: int | None = Query(None, description="Optional: filter by document"),
    db: Session = Depends(get_session),
) -> list[QuestionOut]:
    """List questions for quiz: by user_id, optionally by document_id."""
    if document_id is not None:
        concept_ids = select(Concept.id).where(Concept.document_id == document_id)
    else:
        doc_ids = select(Document.id).where(Document.user_id == user_id)
        concept_ids = select(Concept.id).where(Concept.document_id.in_(doc_ids))
    questions = db.exec(select(Question).where(Question.concept_id.in_(concept_ids))).all()
    return [QuestionOut.model_validate(x) for x in questions]
