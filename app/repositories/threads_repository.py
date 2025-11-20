from app.repositories.base import BaseRepository
from app.models.threads import ThreadInDB
from datetime import datetime
from typing import List
from bson import ObjectId

class ThreadRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, "threads")
        self.collection = db["threads"]
        self.participation = db["participation"]

    async def create_thread(self, payload: dict) -> dict:
        now = datetime.utcnow()
        doc = {
            "channel_id": payload["channel_id"],
            "title": payload["title"],
            "created_by": payload["created_by"],
            "metadata": payload.get("metadata", {}),
            "created_at": now,
            "last_activity": now,
            "message_count": 0,
            "attachments": []
        }
        inserted_id = await self.insert_one(doc)
        doc["_id"] = inserted_id
        return doc

    async def list_threads_by_channel(self, channel_id: str, limit: int = 50) -> List[dict]:
        docs = await self.find_many({"channel_id": channel_id}, sort=[("last_activity", -1)], limit=limit)
        return docs

    async def get_thread(self, thread_id: str) -> dict | None:
        return await self.find_one({"_id": thread_id})

    async def inc_message_count(self, thread_id: str):
        await self.update_one({"_id": thread_id}, {"$inc": {"message_count": 1}, "$set": {"last_activity": datetime.utcnow()}})

    async def add_attachment(self, thread_id: str, attachment: dict):
        await self.update_one({"_id": thread_id}, {"$push": {"attachments": attachment}, "$set": {"last_activity": datetime.utcnow()}})

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

        participated = self.participation.find({"user_id": user_id})

        # threads en los que participó
        participated_ids = set()
        async for p in participated:
            participated_ids.add(p["thread_id"])

        participated_threads = self.collection.find(
            {"_id": {"$in": list(participated_ids)}}
        )

        return {
            "created": [doc async for doc in created],
            "participated": [doc async for doc in participated_threads]
        }
