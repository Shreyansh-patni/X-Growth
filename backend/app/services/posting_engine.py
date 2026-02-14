import asyncio
import logging
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.reply import ReplyCandidate, ReplyHistory, ReplyStatus
from app.models.scheduled_tweet import ScheduledTweet, ScheduledTweetStatus
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
        """
        Process both Reply Candidates and Scheduled Tweets.
        """
        await self._process_reply_candidates()
        await self._process_scheduled_tweets()

    async def _process_reply_candidates(self):
        # 1. Fetch approved, unposted reply candidates
        candidates = self.db.query(ReplyCandidate).filter(
            ReplyCandidate.user_id == self.user.id,
            ReplyCandidate.is_approved == True,
            ~ReplyCandidate.reply_history.has() 
        ).order_by(ReplyCandidate.quality_score.desc()).limit(5).all()

        if not candidates:
            return

        for candidate in candidates:
            # Check Global Rate Limit
            if not self.rate_limiter.check_and_consume(tokens_needed=1.0):
                logger.info(f"Rate limit reached for user {self.user.x_username}. skipping posting.")
                break 

            # Post to X
            try:
                logger.info(f"Posting reply to tweet {candidate.tweet.x_tweet_id}...")
                
                if not candidate.tweet.x_tweet_id:
                    logger.error(f"Missing original tweet ID for candidate {candidate.id}")
                    continue

                response = await self.api_client.post_reply(
                    reply_text=candidate.generated_text,
                    reply_to_tweet_id=candidate.tweet.x_tweet_id
                )
                
                # Log Success
                history = ReplyHistory(
                    reply_candidate_id=candidate.id,
                    user_id=self.user.id,
                    tweet_id=candidate.tweet_id,
                    posted_x_tweet_id=response.get("data", {}).get("id"),
                    posted_text=candidate.generated_text,
                    status=ReplyStatus.posted,
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
                    status=ReplyStatus.failed,
                    error_message=str(e)
                )
                self.db.add(history)
                self.db.commit()
            
            await asyncio.sleep(5) 

    async def _process_scheduled_tweets(self):
        now = datetime.now()
        tweets = self.db.query(ScheduledTweet).filter(
            ScheduledTweet.user_id == self.user.id,
            ScheduledTweet.status == ScheduledTweetStatus.pending,
            ScheduledTweet.scheduled_for <= now
        ).all()
        
        for tweet in tweets:
             # Check Rate Limit (Separate bucket? For now share same)
            if not self.rate_limiter.check_and_consume(tokens_needed=1.0):
                logger.info(f"Rate limit reached during scheduled posting for {self.user.x_username}.")
                break

            try:
                logger.info(f"Posting scheduled tweet {tweet.id}...")
                response = await self.api_client.post_tweet(text=tweet.content)
                
                tweet.status = ScheduledTweetStatus.posted
                tweet.posted_tweet_id = response.get("data", {}).get("id")
                self.db.commit()
                
            except Exception as e:
                logger.error(f"Failed to post scheduled tweet {tweet.id}: {e}")
                tweet.status = ScheduledTweetStatus.failed
                tweet.error_message = str(e)
                self.db.commit()
            
            await asyncio.sleep(2)
