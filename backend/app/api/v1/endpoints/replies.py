from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.reply import ReplyCandidate, ReplyHistory
from app.schemas.reply import ReplyCandidateOut, ReplyCandidateUpdate
from app.services.posting_engine import PostingEngineService

router = APIRouter()

@router.get("/", response_model=List[ReplyCandidateOut])
def read_reply_candidates(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    status: str = "pending" # pending, approved, rejected
) -> Any:
    query = db.query(ReplyCandidate)
    
    if status == "pending":
        query = query.filter(ReplyCandidate.is_approved == False, ReplyCandidate.is_rejected == False)
    elif status == "approved":
        query = query.filter(ReplyCandidate.is_approved == True)
    elif status == "rejected":
        query = query.filter(ReplyCandidate.is_rejected == True)
        
    candidates = query.offset(skip).limit(limit).all()
    
    # Enrich with tweet text
    results = []
    for c in candidates:
        c.tweet_text = c.tweet.full_text if c.tweet else "Unknown Tweet"
        results.append(c)
        
    return results

@router.post("/{reply_id}/approve", response_model=ReplyCandidateOut)
def approve_reply(
    reply_id: str,
    db: Session = Depends(deps.get_db),
    # current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    reply = db.query(ReplyCandidate).filter(ReplyCandidate.id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
        
    reply.is_approved = True
    reply.is_rejected = False
    # reply.approved_at = func.now() # Handled by service if needed or DB default? Model doesn't have default.
    from sqlalchemy.sql import func
    reply.approved_at = func.now()
    
    db.commit()
    db.refresh(reply)
    reply.tweet_text = reply.tweet.full_text if reply.tweet else "Unknown Tweet"
    
    # Trigger Posting Engine (Optional: or let the background loop pick it up)
    # Background loop picks it up.
    
    return reply

@router.post("/{reply_id}/reject", response_model=ReplyCandidateOut)
def reject_reply(
    reply_id: str,
    db: Session = Depends(deps.get_db),
) -> Any:
    reply = db.query(ReplyCandidate).filter(ReplyCandidate.id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
        
    reply.is_approved = False
    reply.is_rejected = True
    
    db.commit()
    db.refresh(reply)
    reply.tweet_text = reply.tweet.full_text if reply.tweet else "Unknown Tweet"
    return reply

@router.put("/{reply_id}", response_model=ReplyCandidateOut)
def update_reply(
    reply_id: str,
    reply_in: ReplyCandidateUpdate,
    db: Session = Depends(deps.get_db),
) -> Any:
    reply = db.query(ReplyCandidate).filter(ReplyCandidate.id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    
    if reply_in.generated_text is not None:
        reply.generated_text = reply_in.generated_text
        
    db.commit()
    db.refresh(reply)
    reply.tweet_text = reply.tweet.full_text if reply.tweet else "Unknown Tweet"
    return reply
