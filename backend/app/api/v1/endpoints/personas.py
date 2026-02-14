from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.persona import Persona
from app.schemas.persona import PersonaCreate, PersonaUpdate, PersonaOut
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[PersonaOut])
def read_personas(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    # In real app filter by current_user
    personas = db.query(Persona).offset(skip).limit(limit).all()
    return personas

@router.post("/", response_model=PersonaOut)
def create_persona(
    persona_in: PersonaCreate,
    db: Session = Depends(deps.get_db),
) -> Any:
    user = db.query(User).first()
    if not user:
         raise HTTPException(status_code=400, detail="No user found")

    # If setting to active, deactivate others
    if persona_in.is_active:
        db.query(Persona).filter(Persona.user_id == user.id).update({"is_active": False})

    persona = Persona(
        **persona_in.dict(),
        user_id=user.id
    )
    db.add(persona)
    db.commit()
    db.refresh(persona)
    return persona

@router.put("/{persona_id}", response_model=PersonaOut)
def update_persona(
    persona_id: str,
    persona_in: PersonaUpdate,
    db: Session = Depends(deps.get_db),
) -> Any:
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    if persona_in.is_active:
         db.query(Persona).filter(Persona.user_id == persona.user_id).update({"is_active": False})

    update_data = persona_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(persona, field, value)

    db.add(persona)
    db.commit()
    db.refresh(persona)
    return persona

@router.delete("/{persona_id}", response_model=PersonaOut)
def delete_persona(
    persona_id: str,
    db: Session = Depends(deps.get_db),
) -> Any:
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    db.delete(persona)
    db.commit()
    return persona
