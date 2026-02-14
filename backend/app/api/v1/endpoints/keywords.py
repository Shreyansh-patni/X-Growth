from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.keyword import Keyword
from app.schemas.keyword import KeywordCreate, KeywordUpdate, KeywordOut
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[KeywordOut])
def read_keywords(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    # In a real app, filter by current_user
    keywords = db.query(Keyword).offset(skip).limit(limit).all()
    return keywords

@router.post("/", response_model=KeywordOut)
def create_keyword(
    keyword_in: KeywordCreate,
    db: Session = Depends(deps.get_db),
    # current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    # Temporary: fetch first user as owner
    user = db.query(User).first()
    if not user:
         raise HTTPException(status_code=400, detail="No user found to assign keyword to")

    keyword = Keyword(
        keyword=keyword_in.keyword,
        is_active=keyword_in.is_active,
        user_id=user.id
    )
    db.add(keyword)
    db.commit()
    db.refresh(keyword)
    return keyword

@router.delete("/{keyword_id}", response_model=KeywordOut)
def delete_keyword(
    keyword_id: str,
    db: Session = Depends(deps.get_db),
) -> Any:
    keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")
    
    db.delete(keyword)
    db.commit()
    return keyword
