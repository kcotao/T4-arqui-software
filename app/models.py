from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from typing import Optional
from datetime import datetime
import uuid

def gen_uuid() -> str:
    return str(uuid.uuid4())

class Channel(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    is_active: bool = True
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ThreadStatus(str):
    OPEN = "open"
    ARCHIVED = "archived"

class Thread(SQLModel, table=True):
    id: str = Field(default_factory=gen_uuid, primary_key=True)
    channel_id: str = Field(index=True, foreign_key="channel.id")
    title: str
    created_by: str
    status: str = Field(default=ThreadStatus.OPEN)
    # evita el nombre reservado "metadata"
    meta: Optional[dict] = Field(default=None, sa_column=Column("metadata", JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None
