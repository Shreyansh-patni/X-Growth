from sqlalchemy.orm import Session
from app.services.x_api_client import XAPIClient
from app.services.tweet_processor import TweetProcessor
from app.models.user import User
from app.models.tweet import TweetSource
import logging

logger = logging.getLogger(__name__)

class MonitorService:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        self.api_client = XAPIClient(user)
        self.processor = TweetProcessor(db)

    async def monitor_home_timeline(self):
        try:
            # In a real scenario, we'd fetch the last seen ID from DB
            raw_tweets = await self.api_client.fetch_home_timeline()
            new_tweets = self.processor.process_tweets(
                raw_tweets, 
                source=TweetSource.home_timeline, 
                user_id=self.user.id
            )
            logger.info(f"Processed {len(new_tweets)} new tweets from home timeline for user {self.user.x_username}")
            return new_tweets
        except Exception as e:
            logger.error(f"Error monitoring home timeline: {e}")
            # Here we would implement error handling / backoff logic
            return []

    async def monitor_lists(self):
        """
        Fetch active lists and monitor them.
        """
        from app.models.monitored_list import MonitoredList
        lists = (
            self.db.query(MonitoredList)
            .filter(MonitoredList.user_id == self.user.id, MonitoredList.is_active == True)
            .all()
        )
        
        total_new_tweets = []
        for lst in lists:
            new_tweets = await self.monitor_list(lst.x_list_id)
            if new_tweets:
                total_new_tweets.extend(new_tweets)
        
        return total_new_tweets

    async def monitor_list(self, list_id: str):
        try:
            raw_tweets = await self.api_client.fetch_list_tweets(list_id)
            new_tweets = self.processor.process_tweets(
                raw_tweets, 
                source=TweetSource.x_list, 
                user_id=self.user.id,
                source_id=list_id # Use list_id as source_id
            )
            logger.info(f"Processed {len(new_tweets)} new tweets from list {list_id} for user {self.user.x_username}")
            return new_tweets
        except Exception as e:
            logger.error(f"Error monitoring list {list_id}: {e}")
            return []

    async def monitor_keywords(self):
        """
        Fetch active keywords and search for new tweets.
        """
        from app.models.keyword import Keyword
        keywords = (
            self.db.query(Keyword)
            .filter(Keyword.user_id == self.user.id, Keyword.is_active == True)
            .all()
        )
        
        total_new_tweets = []
        for kw in keywords:
            try:
                # Basic query: keyword -is:retweet lang:en
                query = f"{kw.keyword} -is:retweet lang:en"
                
                logger.info(f"Searching for keyword: {kw.keyword}")
                raw_tweets = await self.api_client.search_tweets(query)
                
                new_tweets_for_kw = self.processor.process_tweets(
                    raw_tweets,
                    source=TweetSource.keyword_search,
                    user_id=self.user.id
                )
                
                if new_tweets_for_kw:
                    kw.mentions_count += len(new_tweets_for_kw)
                    self.db.commit()
                    
                total_new_tweets.extend(new_tweets_for_kw)
                
            except Exception as e:
                logger.error(f"Error monitoring keyword {kw.keyword}: {e}")
                continue
                
        return total_new_tweets
