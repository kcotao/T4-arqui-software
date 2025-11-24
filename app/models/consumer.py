from typing import Optional
from datetime import datetime
from beanie import Document, PydanticObjectId
from pydantic import Field

class Channel(Document):
    id: PydanticObjectId = Field(alias="_id") 
    name: str
    is_active: bool = True

    class Settings:
        name = "channels" 