import hashlib
from sqlalchemy.orm import Session
from app.models.tweet import Tweet, TweetSource
from app.schemas.tweet import TweetCreate
from app.crud.base import CRUDBase
from app.models.user import User
from typing import List, Optional

class TweetProcessor:
    def __init__(self, db: Session):
        self.db = db

    def calculate_content_hash(self, text: str, author_id: str) -> str:
        return hashlib.sha256(f"{text}{author_id}".encode()).hexdigest()

    def is_duplicate(self, content_hash: str) -> bool:
        return self.db.query(Tweet).filter(Tweet.content_hash == content_hash).first() is not None

    def process_tweets(self, raw_tweets: List[dict], source: TweetSource, user_id: str, source_id: Optional[str] = None) -> List[Tweet]:
        new_tweets = []
        data = raw_tweets.get("data", [])
        includes = raw_tweets.get("includes", {})
        users = {u["id"]: u for u in includes.get("users", [])}

        for item in data:
            author_id = item["author_id"]
            author = users.get(author_id, {})
            content_hash = self.calculate_content_hash(item["text"], author_id)

            if self.is_duplicate(content_hash):
                continue

            # Check if tweet already exists by ID (double check)
            if self.db.query(Tweet).filter(Tweet.x_tweet_id == item["id"]).first():
                continue

            tweet = Tweet(
                x_tweet_id=item["id"],
                user_id=user_id,
                author_x_user_id=author_id,
                author_x_username=author.get("username", "unknown"),
                full_text=item["text"],
                tweet_url=f"https://twitter.com/{author.get('username', 'user')}/status/{item['id']}",
                source=source,
                source_id=source_id,
                content_hash=content_hash,
                metadata_=item
            )
            self.db.add(tweet)
            new_tweets.append(tweet)
        
        if new_tweets:
            self.db.commit()
            for t in new_tweets:
                 self.db.refresh(t)
        
        return new_tweets
