from app.repositories.base import BaseRepository
from app.models.threads import ThreadInDB
from datetime import datetime
from typing import List
import uuid
from bson import errors, ObjectId
from pymongo.results import DeleteResult

class ThreadRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, "threads")
        self.collection = db["threads"]
        self.participation = db["participation"]

    async def create_thread(self, channel_id, thread_name, user_id) -> dict:
        
        now = datetime.utcnow()

        generated_uid = str(uuid.uuid4())

        doc = {
            "channel_id": channel_id,
            "uuid": generated_uid,
            "title": thread_name,
            "created_by": user_id,
            "created_at": now,
            "last_activity": now,
            "message_count": 0,
            "attachments": []
        }
        inserted_id = await self.insert_one(doc)

        doc_to_return = {
            "thread_id": str(inserted_id),
            "channel_id": channel_id,
            "uuid": generated_uid,
            "title": thread_name,
            "created_by": user_id,
            "created_at": now,
            "last_activity": now,
            "message_count": 0,
            "attachments": []
        }
        return doc_to_return

    async def list_threads_by_channel(self, channel_id: str, limit: int = 50) -> List[dict]:
        docs = await self.find_many({"channel_id": channel_id}, sort=[("last_activity", -1)], limit=limit)
        return docs

    async def get_thread(self, thread_id: str) -> dict | None:
        doc = await self.find_one({"_id": ObjectId(thread_id)})
        if doc:
            doc["thread_id"] = str(doc["_id"])
            del doc["_id"]
            return doc
        return None
    

    async def inc_message_count(self, thread_id: str):
        await self.update_one({"thread_id": thread_id}, {"$inc": {"message_count": 1}, "$set": {"last_activity": datetime.utcnow()}})

    async def add_attachment(self, thread_id: str, attachment: dict):
        await self.update_one({"thread_id": thread_id}, {"$push": {"attachments": attachment}, "$set": {"last_activity": datetime.utcnow()}})

    async def update_by_id(self, thread_id: str, update_data: dict):
        return await self.collection.update_one(
            {"_id": ObjectId(thread_id)},
            update_data,
            )

    async def get_by_id(self, thread_id: str):
        return await self.collection.find_one({"_id": ObjectId(thread_id)})
    
    async def edit_thread(self, thread_id: str, update_data: dict):
        result = await self.collection.update_one(
            {"_id": ObjectId(thread_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0

    async def get_user_threads(self, user_id: str):
        created = self.collection.find({"created_by": user_id})
        threads_list = []

        async for doc in created:

            doc["thread_id"] = str(doc["_id"])
            del doc["_id"]
            threads_list.append(doc)
        
        return {
        "created": threads_list,
         }
    
    async def get_threads(self, channel_id: str) -> dict | None:
        try:
            oid = channel_id
        except errors.InvalidId:
            return []
        
        cursor = self.collection.find({"channel_id": oid})
        
        threads = await cursor.to_list(length=None)

        for thread in threads:
            thread["thread_id"] = str(thread["_id"])
            if "channel_id" in thread:
                thread["channel_id"] = str(thread["channel_id"])

        return threads

    async def delete_thread(self, thread_id: str) -> DeleteResult:
    
        mongo_id = ObjectId(thread_id)
        result = await self.collection.delete_one({"_id": mongo_id})
    
        return result