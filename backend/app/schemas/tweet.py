from pydantic import BaseModel, UUID4, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.tweet import TweetSource

class TweetBase(BaseModel):
    x_tweet_id: str
    author_x_user_id: str
    author_x_username: str
    full_text: str
    tweet_url: str
    source: TweetSource
    source_id: Optional[UUID4] = None
    metadata_: Dict[str, Any] = {} # Mapped to 'metadata' in DB

    class Config:
        from_attributes = True

class TweetCreate(TweetBase):
    user_id: UUID4
    content_hash: str

class TweetUpdate(BaseModel):
    is_processed: Optional[bool] = None
    processed_at: Optional[datetime] = None

class TweetInDB(TweetBase):
    id: UUID4
    user_id: UUID4
    detected_at: datetime
    is_processed: bool
    processed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
