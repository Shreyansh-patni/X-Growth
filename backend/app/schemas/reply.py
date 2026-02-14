from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class ReplyCandidateBase(BaseModel):
    tweet_id: UUID
    generated_text: str
    llm_model_used: Optional[str] = None
    safety_score: float = 0.0

class ReplyCandidateUpdate(BaseModel):
    is_approved: Optional[bool] = None
    is_rejected: Optional[bool] = None
    generated_text: Optional[str] = None # Allow editing before approval

class ReplyCandidateOut(ReplyCandidateBase):
    id: UUID
    is_approved: bool
    is_rejected: bool
    generated_at: datetime
    quality_score: float
    tweet_text: Optional[str] = None # Calculated field

    class Config:
        orm_mode = True
