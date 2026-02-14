from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from uuid import UUID

class ScheduledTweetBase(BaseModel):
    content: str
    scheduled_for: datetime
    media_urls: Optional[List[str]] = []

class ScheduledTweetCreate(ScheduledTweetBase):
    pass

class ScheduledTweetUpdate(BaseModel):
    content: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    media_urls: Optional[List[str]] = None
    status: Optional[str] = None

class ScheduledTweetOut(ScheduledTweetBase):
    id: UUID
    user_id: UUID
    status: str
    error_message: Optional[str] = None
    posted_tweet_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
