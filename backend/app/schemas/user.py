from pydantic import BaseModel, UUID4, EmailStr
from typing import Optional
from datetime import datetime
from decimal import Decimal

class UserBase(BaseModel):
    x_username: str
    is_active: bool = True
    ai_rules: dict = {}

class UserCreate(UserBase):
    x_user_id: str
    password: str
    access_token: str
    access_token_secret: str

class UserUpdate(BaseModel):
    x_username: Optional[str] = None
    is_active: Optional[bool] = None
    is_paused: Optional[bool] = None
    daily_reply_cap: Optional[int] = None
    ai_rules: Optional[dict] = None

class UserInDBBase(UserBase):
    id: UUID4
    x_user_id: str
    account_health_score: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass
