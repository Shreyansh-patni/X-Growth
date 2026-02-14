from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class KeywordBase(BaseModel):
    keyword: str
    is_active: bool = True

class KeywordCreate(KeywordBase):
    pass

class KeywordUpdate(KeywordBase):
    pass

class KeywordOut(KeywordBase):
    id: UUID
    user_id: UUID
    mentions_count: int
    last_crawled_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        orm_mode = True
