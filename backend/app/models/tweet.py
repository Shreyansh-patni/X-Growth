from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base

class TweetSource(str, enum.Enum):
    home_timeline = "home_timeline"
    x_list = "x_list"
    keyword_search = "keyword_search"

class XList(Base):
    __tablename__ = "x_lists"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    list_id = Column(String(255), unique=True, nullable=False, index=True)
    list_name = Column(String(255), nullable=False)
    list_url = Column(String, nullable=False)
    description = Column(String)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    tweets = relationship("Tweet", back_populates="source_list")


class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    x_tweet_id = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    author_x_user_id = Column(String(255), nullable=False)
    author_x_username = Column(String(255), nullable=False)
    full_text = Column(String, nullable=False)
    tweet_url = Column(String, nullable=False)
    source = Column(Enum(TweetSource), nullable=False, index=True)
    source_id = Column(UUID(as_uuid=True), ForeignKey("x_lists.id", ondelete="SET NULL"))
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    processed_at = Column(DateTime(timezone=True))
    is_processed = Column(Boolean, default=False, nullable=False, index=True)
    content_hash = Column(String(64), unique=True, nullable=False)
    metadata_ = Column("metadata", JSONB, default={}, nullable=False) # 'metadata' is reserved in SQLAlchemy Base
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("app.models.user.User", back_populates="tweets")
    source_list = relationship("XList", back_populates="tweets")
    reply_candidates = relationship("app.models.reply.ReplyCandidate", back_populates="tweet")
    reply_history = relationship("app.models.reply.ReplyHistory", back_populates="tweet")
