from sqlalchemy.orm import Session
from app.models.reply import ReplyCandidate
import logging

logger = logging.getLogger(__name__)

class SafetyClassifierService:
    def __init__(self, db: Session):
        self.db = db

    async def classify_reply(self, candidate: ReplyCandidate) -> float:
        # For MVP, we'll implement a basic keyword-based safety check
        # In production, this would call Perspective API or a moderation model
        
        unsafe_keywords = ["scam", "crypto", "dm me", "follow back", "illegal"]
        text_lower = candidate.generated_text.lower()
        
        score = 100.0
        for word in unsafe_keywords:
            if word in text_lower:
                score -= 50.0 # Heavy penalty
        
        candidate.safety_score = max(0.0, score)
        
        # Auto-reject if unsafe
        if candidate.safety_score < 50:
             candidate.is_rejected = True
             candidate.rejection_reason = "Safety check failed"

        self.db.add(candidate)
        self.db.commit()
        return candidate.safety_score
