from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

# Shared properties
class MonitoredListBase(BaseModel):
    x_list_id: str
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True

# Properties to receive on creation
class MonitoredListCreate(MonitoredListBase):
    pass

# Properties to receive on update
class MonitoredListUpdate(BaseModel):
    is_active: Optional[bool] = None

# Properties shared by models stored in DB
class MonitoredListInDBBase(MonitoredListBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Properties to return to client
class MonitoredList(MonitoredListInDBBase):
    pass

# Response for available lists from X
class XListResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    member_count: int
    follower_count: int
