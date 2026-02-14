from sqlalchemy.orm import Session
from app.models.user import User
from app.services.x_api_client import XAPIClient
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        self.api_client = XAPIClient(user)

    async def generate_audit_report(self) -> Dict[str, Any]:
        """
        Fetch recent tweets and calculate account health metrics.
        """
        try:
            # 1. Fetch last 50 tweets
            data = await self.api_client.fetch_user_tweets(max_results=50)
            tweets = data.get("data", [])
            
            if not tweets:
                return self._empty_report()

            # 2. Aggregate Metrics
            total_impressions = 0
            total_engagements = 0
            total_likes = 0
            total_replies = 0
            total_retweets = 0
            
            processed_tweets = []

            for t in tweets:
                metrics = t.get("public_metrics", {})
                # Note: 'impression_count' is in public_metrics for own tweets in v2
                impressions = metrics.get("impression_count", 0) 
                likes = metrics.get("like_count", 0)
                replies = metrics.get("reply_count", 0)
                retweets = metrics.get("retweet_count", 0)
                
                # Simple Engagement: sum of actions
                engagement = likes + replies + retweets
                
                total_impressions += impressions
                total_engagements += engagement
                total_likes += likes
                total_replies += replies
                total_retweets += retweets
                
                # Calculate individual ER
                er = 0
                if impressions > 0:
                    er = (engagement / impressions) * 100
                
                processed_tweets.append({
                    "id": t["id"],
                    "text": t["text"],
                    "created_at": t["created_at"],
                    "impressions": impressions,
                    "engagement": engagement,
                    "engagement_rate": round(er, 2),
                    "likes": likes,
                    "replies": replies,
                    "retweets": retweets
                })

            # 3. Calculate Global Metrics
            avg_er = 0
            if total_impressions > 0:
                avg_er = (total_engagements / total_impressions) * 100
            
            # 4. Identify Top Tweets
            top_tweets = sorted(processed_tweets, key=lambda x: x["engagement"], reverse=True)[:5]
            
            return {
                "summary": {
                    "total_tweets": len(tweets),
                    "total_impressions": total_impressions,
                    "total_engagements": total_engagements,
                    "average_engagement_rate": round(avg_er, 2),
                    "total_likes": total_likes,
                    "total_replies": total_replies,
                    "total_retweets": total_retweets
                },
                "top_tweets": top_tweets,
                "recent_history": processed_tweets # For graphs
            }

        except Exception as e:
            logger.error(f"Audit failed for {self.user.x_username}: {e}")
            raise e

    def _empty_report(self):
        return {
            "summary": {
                "total_tweets": 0,
                "total_impressions": 0,
                "average_engagement_rate": 0,
            },
            "top_tweets": [],
            "recent_history": []
        }
