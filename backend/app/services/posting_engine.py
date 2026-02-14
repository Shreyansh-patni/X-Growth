import asyncio
import logging
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.reply import ReplyCandidate, ReplyHistory
from app.services.x_api_client import XAPIClient
from app.services.rate_limiter import RateLimiterService

logger = logging.getLogger(__name__)

class PostingEngineService:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        self.api_client = XAPIClient(user)
        self.rate_limiter = RateLimiterService(db, user)

    async def process_queue(self):
        # 1. Fetch approved, unposted reply candidates
        candidates = self.db.query(ReplyCandidate).filter(
            ReplyCandidate.user_id == self.user.id,
            ReplyCandidate.is_approved == True,
            # We need a way to check if already posted. 
            # In the schema, ReplyHistory links to ReplyCandidate.
            # So checking if ReplyHistory exists for this candidate.
            ~ReplyCandidate.reply_history.has() 
        ).order_by(ReplyCandidate.quality_score.desc()).limit(5).all()

        if not candidates:
            return

        for candidate in candidates:
            # 2. Check Global Rate Limit (Token Bucket)
            if not self.rate_limiter.check_and_consume(tokens_needed=1.0):
                logger.info(f"Rate limit reached for user {self.user.x_username}. skipping posting.")
                break # Stop processing queue for now

            # 3. Check Cooldown (5 replies then 60s logic)
            # This logic mimics the rate limiter's refill rate essentially 
            # but usually enforces a stricter "stop" after a batch.
            # Our Token Bucket with capacity=5 and refill=1/12s approximates this.
            # For strict "wait 60s after 5", we'd need extra state tracking.
            # Detailed implementation of strict batch cooling:
            # Check RateLimit.current_burst_count
            
            # 4. Post to X
            try:
                logger.info(f"Posting reply to tweet {candidate.tweet.x_tweet_id}...")
                
                # Verify we have original tweet ID
                if not candidate.tweet.x_tweet_id:
                    logger.error(f"Missing original tweet ID for candidate {candidate.id}")
                    continue

                response = await self.api_client.post_reply(
                    reply_text=candidate.generated_text,
                    reply_to_tweet_id=candidate.tweet.x_tweet_id
                )
                
                # 5. Log Success
                history = ReplyHistory(
                    reply_candidate_id=candidate.id,
                    user_id=self.user.id,
                    tweet_id=candidate.tweet_id,
                    posted_x_tweet_id=response.get("data", {}).get("id"),
                    posted_text=candidate.generated_text,
                    status="SUCCESS",
                    response_metadata=response
                )
                self.db.add(history)
                self.db.commit()
                
            except Exception as e:
                logger.error(f"Failed to post reply: {e}")
                # Log Failure
                history = ReplyHistory(
                    reply_candidate_id=candidate.id,
                    user_id=self.user.id,
                    tweet_id=candidate.tweet_id,
                    posted_text=candidate.generated_text,
                    status="FAILED",
                    error_message=str(e)
                )
                self.db.add(history)
                self.db.commit()
            
            # Random delay between posts in a batch
            await asyncio.sleep(5) 
