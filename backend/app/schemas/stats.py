from pydantic import BaseModel
from datetime import date
from uuid import UUID

class UserStatsBase(BaseModel):
    date: date
    follower_count: int
    following_count: int
    tweet_count: int
    followers_gained: int

class UserStatsCreate(UserStatsBase):
    pass

class UserStatsOut(UserStatsBase):
    id: UUID
    user_id: UUID

    class Config:
        orm_mode = True

class DashboardStats(BaseModel):
    total_tweets_monitored: int
    total_replies_generated: int
    total_replies_posted: int
    current_followers: int
    followers_gained_today: int
