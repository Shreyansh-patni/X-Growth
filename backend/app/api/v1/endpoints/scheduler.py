from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps
from app.models.scheduled_tweet import ScheduledTweet, ScheduledTweetStatus
from uuid import UUID
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[schemas.ScheduledTweet])
def read_scheduled_tweets(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve scheduled tweets.
    """
    tweets = (
        db.query(ScheduledTweet)
        .filter(ScheduledTweet.user_id == current_user.id)
        .order_by(ScheduledTweet.scheduled_for.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return tweets

@router.post("/", response_model=schemas.ScheduledTweet)
def create_scheduled_tweet(
    tweet_in: schemas.ScheduledTweetCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Schedule a new tweet.
    """
    tweet = ScheduledTweet(
        user_id=current_user.id,
        content=tweet_in.content,
        scheduled_for=tweet_in.scheduled_for,
        media_urls=tweet_in.media_urls,
        status=ScheduledTweetStatus.pending
    )
    db.add(tweet)
    db.commit()
    db.refresh(tweet)
    return tweet

@router.put("/{tweet_id}", response_model=schemas.ScheduledTweet)
def update_scheduled_tweet(
    tweet_id: UUID,
    tweet_in: schemas.ScheduledTweetUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a scheduled tweet.
    """
    tweet = db.query(ScheduledTweet).filter(
        ScheduledTweet.id == tweet_id,
        ScheduledTweet.user_id == current_user.id
    ).first()
    
    if not tweet:
        raise HTTPException(status_code=404, detail="Scheduled tweet not found")
        
    if tweet.status == ScheduledTweetStatus.posted:
         raise HTTPException(status_code=400, detail="Cannot edit a posted tweet")

    if tweet_in.content is not None:
        tweet.content = tweet_in.content
    if tweet_in.scheduled_for is not None:
        tweet.scheduled_for = tweet_in.scheduled_for
    if tweet_in.media_urls is not None:
        tweet.media_urls = tweet_in.media_urls
        
    db.commit()
    db.refresh(tweet)
    return tweet

@router.delete("/{tweet_id}", response_model=schemas.ScheduledTweet)
def delete_scheduled_tweet(
    tweet_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a scheduled tweet.
    """
    tweet = db.query(ScheduledTweet).filter(
        ScheduledTweet.id == tweet_id,
        ScheduledTweet.user_id == current_user.id
    ).first()
    
    if not tweet:
        raise HTTPException(status_code=404, detail="Scheduled tweet not found")
        
    db.delete(tweet)
    db.commit()
    return tweet
