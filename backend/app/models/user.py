from sqlalchemy import Column, String, Boolean, DateTime, Numeric, Integer, ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    x_user_id = Column(String(255), unique=True, nullable=False, index=True)
    x_username = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    access_token = Column(String, nullable=True) # Check if nullable needed, initially maybe not but strictness varies
    access_token_secret = Column(String, nullable=True) # Kept for backward compat or if needed
    refresh_token = Column(String, nullable=True) # OAuth 2.0
    account_health_score = Column(Numeric(5, 2), default=100.00, nullable=False)
    last_health_check_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_paused = Column(Boolean, default=False, nullable=False)
    daily_reply_cap = Column(Integer, default=100, nullable=False)
    current_daily_replies = Column(Integer, default=0, nullable=False)
    last_daily_cap_reset_at = Column(Date, default=func.current_date(), nullable=False)
    ai_rules = Column(JSONB, default={}, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    tweets = relationship("Tweet", back_populates="user")
    rate_limits = relationship("RateLimit", uselist=False, back_populates="user")
    credits = relationship("Credit", back_populates="user")
    reply_candidates = relationship("ReplyCandidate", back_populates="user")
    reply_history = relationship("ReplyHistory", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    keywords = relationship("app.models.keyword.Keyword", back_populates="user")
    personas = relationship("app.models.persona.Persona", back_populates="user")
    monitored_lists = relationship("app.models.monitored_list.MonitoredList", back_populates="user")


class RateLimit(Base):
    __tablename__ = "rate_limits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    tokens = Column(Numeric(10, 4), default=0.0, nullable=False)
    last_refill_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    capacity = Column(Numeric(10, 4), default=5.0, nullable=False)
    refill_rate = Column(Numeric(10, 4), default=0.0833, nullable=False)
    burst_limit = Column(Integer, default=5, nullable=False)
    current_burst_count = Column(Integer, default=0, nullable=False)
    last_burst_reset_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="rate_limits")


class Credit(Base):
    __tablename__ = "credits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    credit_type = Column(String(50), nullable=False)
    amount = Column(Numeric(10, 4), nullable=False)
    transaction_type = Column(String(50), nullable=False)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    user = relationship("User", back_populates="credits")
