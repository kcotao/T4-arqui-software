from pydantic import BaseModel

class ThreadClassification(BaseModel):
    label: str  # "important", "inappropriate", etc.

class AdminThreadStatus(BaseModel):
    active: bool