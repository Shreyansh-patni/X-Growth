from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api import deps
from app.models.tweet import Tweet
from app.models.reply import ReplyCandidate, ReplyHistory
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
def read_stats(
    db: Session = Depends(deps.get_db),
    # current_user: User = Depends(deps.get_current_active_user), # Optional: secure this
) -> Any:
    # MVP: Global stats or first user stats if no auth
    # For now, let's just count everything.
    
    total_tweets_monitored = db.query(Tweet).count()
    total_replies_generated = db.query(ReplyCandidate).count()
    total_replies_posted = db.query(ReplyHistory).filter(ReplyHistory.status == "SUCCESS").count()
    
    # Calculate "Active Now" as tweets in last hour? 
    # Or just return static/calculated data.
    
    return {
        "total_tweets_monitored": total_tweets_monitored,
        "total_replies_generated": total_replies_generated,
        "total_replies_posted": total_replies_posted,
        "system_status": "active"
    }

@router.get("/recent", response_model=Dict[str, Any])
def read_recent_activity(
    db: Session = Depends(deps.get_db),
) -> Any:
    recent_replies = db.query(ReplyHistory).order_by(ReplyHistory.created_at.desc()).limit(5).all()
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
