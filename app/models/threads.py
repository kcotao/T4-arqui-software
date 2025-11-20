from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

# ---- ObjectId compatibility ----

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return str(v)

# ---- Request model for creating threads ----

class ThreadCreate(BaseModel):
    channel_id: str
    title: str
    created_by: str
    metadata: Optional[dict] = None


# ---- Model representing stored document ----
class ThreadInDB(BaseModel):
    id: PyObjectId = Field(default=None, alias="_id")
    channel_id: str
    title: str
    created_by: str
    created_at: datetime
    last_activity: datetime
    message_count: int = 0
    attachments: List[dict] = []

    # NEW FEATURES
    likes: int = 0
    liked_by: List[str] = []
    saved_by: List[str] = []
    shared_count: int = 0
    replies: List[dict] = []

    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
        "json_encoders": {
            ObjectId: str,
            PyObjectId: str,
        }
    }



# ---- Base model for simple responses ----
class ThreadBase(BaseModel):
    title: str
    user_id: str
    channel_id: str


# ---- Partial update model ----

class ThreadEdit(BaseModel):
    title: Optional[str] = None
    metadata: Optional[dict] = None


class ThreadReport(BaseModel):
    reason: str
    reported_by: str


class ThreadHide(BaseModel):
    hidden_by: str

