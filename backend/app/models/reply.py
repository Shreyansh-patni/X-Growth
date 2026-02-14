from sqlalchemy import Column, String, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class ReplyCandidate(Base):
    __tablename__ = "reply_candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tweet_id = Column(UUID(as_uuid=True), ForeignKey("tweets.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    generated_text = Column(String, nullable=False)
    llm_model_used = Column(String(255))
    safety_score = Column(Numeric(5, 2), default=0.00, nullable=False)
    quality_score = Column(Numeric(5, 2), default=0.00, nullable=False)
    is_approved = Column(Boolean, default=False, index=True)
    is_rejected = Column(Boolean, default=False)
    rejection_reason = Column(String)
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    approved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    tweet = relationship("app.models.tweet.Tweet", back_populates="reply_candidates")
    user = relationship("app.models.user.User", back_populates="reply_candidates")
    reply_history = relationship("ReplyHistory", back_populates="reply_candidate", uselist=False)


class ReplyHistory(Base):
    __tablename__ = "reply_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reply_candidate_id = Column(UUID(as_uuid=True), ForeignKey("reply_candidates.id", ondelete="CASCADE"), unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    tweet_id = Column(UUID(as_uuid=True), ForeignKey("tweets.id", ondelete="CASCADE"), nullable=False, index=True)
    posted_x_tweet_id = Column(String(255), unique=True)
    posted_text = Column(String, nullable=False)
    posted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True)
    error_message = Column(String)
    response_metadata = Column(JSONB, default={}, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    reply_candidate = relationship("ReplyCandidate", back_populates="reply_history")
    user = relationship("app.models.user.User", back_populates="reply_history")
    tweet = relationship("app.models.tweet.Tweet", back_populates="reply_history")


class DuplicateReplyEmbedding(Base):
    __tablename__ = "duplicate_reply_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reply_text_hash = Column(String(64), unique=True, nullable=False)
    # Using generic ARRAY/JSONB for now as pgvector needs extension to be installed in DB
    # In production, we would use parsed Vector type
    embedding = Column(ARRAY(Numeric), nullable=False) 
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    user = relationship("app.models.user.User")
