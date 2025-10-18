from pydantic import BaseModel, Field
from typing import Optional, Dict, Literal
from datetime import datetime

class ThreadCreate(BaseModel):
    channel_id: str
    title: str = Field(min_length=1, max_length=200)
    created_by: str
    meta: Optional[Dict] = None

class ThreadUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    status: Optional[Literal["open", "archived"]] = None
    meta: Optional[Dict] = None

class ThreadOut(BaseModel):
    id: str
    channel_id: str
    title: str
    created_by: str
    status: str
    meta: Optional[Dict]
    created_at: datetime
    updated_at: datetime
