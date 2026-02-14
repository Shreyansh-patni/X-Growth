from sqlalchemy.orm import Session
from app.models.user import User, RateLimit
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RateLimiterService:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user

    def _get_or_create_limit(self) -> RateLimit:
        limit = self.db.query(RateLimit).filter(RateLimit.user_id == self.user.id).first()
        if not limit:
            limit = RateLimit(
                user_id=self.user.id,
                tokens=5.0, # Start full
                capacity=5.0,
                refill_rate=0.0833, # 5 tokens / 60 seconds
                last_refill_at=datetime.utcnow()
            )
            self.db.add(limit)
            self.db.commit()
            self.db.refresh(limit)
        return limit

    def check_and_consume(self, tokens_needed: float = 1.0) -> bool:
        limit = self._get_or_create_limit()
        now = datetime.utcnow()
        
        # Refill tokens
        # Ensure last_refill_at is unaware or convert to utc if needed. Model has timezone=True.
        # Assuming database returns aware datetime.
        last_refill = limit.last_refill_at
        if last_refill.tzinfo:
            last_refill = last_refill.replace(tzinfo=None) # simplistic conversion for calc

        time_elapsed = (now - last_refill).total_seconds()
        tokens_to_add = time_elapsed * float(limit.refill_rate)
        
        limit.tokens = min(float(limit.capacity), float(limit.tokens) + tokens_to_add)
        limit.last_refill_at = now
        
        if limit.tokens >= tokens_needed:
            limit.tokens -= tokens_needed
            self.db.commit()
            return True
        else:
            self.db.commit() # Save the refill update even if consume failed
            return False
