from sqlalchemy.orm import Session
from datetime import date
from app.models.stats import UserStats
from app.models.user import User
from app.services.x_api_client import XAPIClient
import logging

logger = logging.getLogger(__name__)

class StatsService:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        self.api_client = XAPIClient(user)

    async def snapshot_daily_stats(self) -> UserStats:
        """
        Fetch current user stats from X and store/update for today.
        """
        try:
            # 1. Fetch current stats from X
            user_data = await self.api_client.fetch_user_me()
            data = user_data["data"]
            metrics = data["public_metrics"]
            
            followers = metrics["followers_count"]
            following = metrics["following_count"]
            tweets = metrics["tweet_count"]
            
            today = date.today()
            
            # 2. Check if stats exist for today
            stats = (
                self.db.query(UserStats)
                .filter(UserStats.user_id == self.user.id, UserStats.date == today)
                .first()
            )
            
            if stats:
                # Update existing
                stats.follower_count = followers
                stats.following_count = following
                stats.tweet_count = tweets
                # Recalculate gained if needed (requires yesterday's data)
            else:
                # Create new
                # Get yesterday's stats for delta
                yesterday_stats = (
                    self.db.query(UserStats)
                    .filter(UserStats.user_id == self.user.id, UserStats.date < today)
                    .order_by(UserStats.date.desc())
                    .first()
                )
                
                gained = 0
                if yesterday_stats:
                    gained = followers - yesterday_stats.follower_count
                
                stats = UserStats(
                    user_id=self.user.id,
                    date=today,
                    follower_count=followers,
                    following_count=following,
                    tweet_count=tweets,
                    followers_gained=gained
                )
                self.db.add(stats)
            
            self.db.commit()
            self.db.refresh(stats)
            return stats
            
        except Exception as e:
            logger.error(f"Failed to snapshot stats for {self.user.x_username}: {e}")
            raise e
