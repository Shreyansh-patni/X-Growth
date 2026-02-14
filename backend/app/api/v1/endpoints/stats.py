from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas
from app.api import deps
from app.models.tweet import Tweet
from app.models.reply import ReplyCandidate, ReplyHistory, ReplyStatus
from app.services.stats_service import StatsService
from datetime import date, timedelta

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
async def read_dashboard_stats(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current dashboard stats.
    """
    # 1. Monitored Tweets (Total)
    total_tweets = db.query(Tweet).count() # Global for now, strictly should be by user's monitored sources
    
    # 2. Replies Generated
    total_generated = db.query(ReplyCandidate).count()
    
    # 3. Replies Posted
    total_posted = db.query(ReplyHistory).filter(ReplyHistory.status == ReplyStatus.posted).count()
    
    # 4. Current User Stats (Followers)
    # Try to get today's stats, if not trigger a fetch
    today = date.today()
    user_stats = db.query(models.UserStats).filter(
        models.UserStats.user_id == current_user.id,
        models.UserStats.date == today
    ).first()
    
    current_followers = 0
    followers_gained = 0
    
    if user_stats:
        current_followers = user_stats.follower_count
        followers_gained = user_stats.followers_gained
    else:
        # Trigger fetch if missing
        try:
            service = StatsService(db, current_user)
            stats = await service.snapshot_daily_stats()
            current_followers = stats.follower_count
            followers_gained = stats.followers_gained
        except Exception:
            pass 

    return {
        "total_tweets_monitored": total_tweets,
        "total_replies_generated": total_generated,
        "total_replies_posted": total_posted,
        "current_followers": current_followers,
        "followers_gained_today": followers_gained
    }

@router.get("/history", response_model=List[schemas.UserStats])
def read_stats_history(
    days: int = 30,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get historical user stats for charts.
    """
    since = date.today() - timedelta(days=days)
    stats = (
        db.query(models.UserStats)
        .filter(
            models.UserStats.user_id == current_user.id,
            models.UserStats.date >= since
        )
        .order_by(models.UserStats.date.asc())
        .all()
    )
    return stats

@router.get("/recent", response_model=Dict[str, Any])
def read_recent_activity(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    # Filter by user (using the relationship back to tweet -> user is hard without direct link on reply history)
    # For MVP, we'll assume global or link via Tweet
    
    recent_replies = (
        db.query(ReplyHistory)
        .join(Tweet)
        .filter(Tweet.author_id != current_user.x_user_id) # Basic filter
        .order_by(ReplyHistory.created_at.desc())
        .limit(5)
        .all()
    )
    
    return {
        "recent_replies": [
            {
                "id": str(r.id),
                "tweet_text": r.tweet.full_text[:50] + "..." if r.tweet else "Unknown",
                "posted_text": r.posted_text,
                "status": r.status,
                "created_at": r.created_at
            }
            for r in recent_replies
        ]
    }
