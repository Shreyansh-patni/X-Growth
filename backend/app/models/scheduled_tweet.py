from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base
import enum

class ScheduledTweetStatus(str, enum.Enum):
    pending = "pending"
    posted = "posted"
    failed = "failed"

class ScheduledTweet(Base):
    __tablename__ = "scheduled_tweets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    content = Column(String, nullable=False)
    scheduled_for = Column(DateTime(timezone=True), nullable=False, index=True)
    
    media_urls = Column(JSON, default=[]) # List of strings
    
    status = Column(String(50), default=ScheduledTweetStatus.pending, index=True)
    error_message = Column(String, nullable=True)
    
    posted_tweet_id = Column(String(255), nullable=True) # X ID after posting
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    user = relationship("app.models.user.User", back_populates="scheduled_tweets")
