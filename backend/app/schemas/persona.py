from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class PersonaBase(BaseModel):
    name: str
    description: Optional[str] = None
    system_prompt: str
    is_active: bool = False

class PersonaCreate(PersonaBase):
    pass

class PersonaUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    is_active: Optional[bool] = None

class PersonaOut(PersonaBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
