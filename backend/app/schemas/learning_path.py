from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class LearningPathCreate(BaseModel):
    title: str = Field(min_length=1, max_length=512)
    description: Optional[str] = None
    hours_per_day: float = Field(default=1.0, ge=0.5, le=8.0)


class DailyStudyPlanOut(BaseModel):
    id: int
    learning_path_id: int
    day_number: int
    title: str
    description: Optional[str]
    chunk_ids: List[int]
    estimated_minutes: int
    created_at: datetime

    model_config = {"from_attributes": True}


class LearningPathOut(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str]
    hours_per_day: float
    total_days: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime
    daily_plans: List[DailyStudyPlanOut] = []

    model_config = {"from_attributes": True}


class LearningPathSummary(BaseModel):
    id: int
    title: str
    description: Optional[str]
    hours_per_day: float
    total_days: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime
    document_count: int = 0

    model_config = {"from_attributes": True}
