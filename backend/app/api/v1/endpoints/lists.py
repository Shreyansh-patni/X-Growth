from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps
from app.services.x_api_client import XAPIClient

router = APIRouter()

@router.get("/available", response_model=List[schemas.list.XListResponse])
async def get_available_lists(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Fetch lists owned by the user from X API.
    """
    client = XAPIClient(current_user)
    try:
        data = await client.fetch_user_owned_lists()
        lists = data.get("data", [])
        return lists
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch lists: {str(e)}")

@router.get("/", response_model=List[schemas.list.MonitoredList])
def read_monitored_lists(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve monitored lists.
    """
    lists = (
        db.query(models.MonitoredList)
        .filter(models.MonitoredList.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return lists

@router.post("/", response_model=schemas.list.MonitoredList)
def create_monitored_list(
    list_in: schemas.list.MonitoredListCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add a list to monitoring.
    """
    # Check if already exists
    existing = (
        db.query(models.MonitoredList)
        .filter(
            models.MonitoredList.user_id == current_user.id,
            models.MonitoredList.x_list_id == list_in.x_list_id
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="List already monitored")

    db_obj = models.MonitoredList(
        user_id=current_user.id,
        x_list_id=list_in.x_list_id,
        name=list_in.name,
        description=list_in.description,
        is_active=list_in.is_active
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.delete("/{id}", response_model=schemas.list.MonitoredList)
def delete_monitored_list(
    id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Stop monitoring a list.
    """
    list_obj = (
        db.query(models.MonitoredList)
        .filter(models.MonitoredList.id == id, models.MonitoredList.user_id == current_user.id)
        .first()
    )
    if not list_obj:
        raise HTTPException(status_code=404, detail="List not found")
        
    db.delete(list_obj)
    db.commit()
    return list_obj
