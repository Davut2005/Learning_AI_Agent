from pydantic import BaseModel


class QuestionOut(BaseModel):
    id: int
    concept_id: int
    question_text: str
    correct_answer: str
    options: dict | None = None

    model_config = {"from_attributes": True}
