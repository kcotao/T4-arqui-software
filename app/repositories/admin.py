from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId


class AdminRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.threads

    async def classify_thread(self, thread_id: str, label: str) -> bool:
        """Clasifica un hilo (important, inappropriate, etc)."""
        result = await self.collection.update_one(
            {"_id": ObjectId(thread_id)},
            {"$set": {"label": label}}
        )
        return result.modified_count == 1

    async def update_thread_status(self, thread_id: str, active: bool) -> bool:
        """Activa o desactiva un hilo."""
        result = await self.collection.update_one(
            {"_id": ObjectId(thread_id)},
            {"$set": {"active": active}}
        )
        return result.modified_count == 1

    async def delete_thread(self, thread_id: str) -> bool:
        """Elimina un hilo permanentemente."""
        result = await self.collection.delete_one({"_id": ObjectId(thread_id)})
        return result.deleted_count == 1

    async def count_threads(self) -> int:
        """Obtiene cantidad total de hilos."""
        return await self.collection.count_documents({})

    async def count_threads_by_user(self, user_id: str) -> int:
        """Obtiene cantidad de hilos creados por un usuario."""
        return await self.collection.count_documents({"user_id": user_id})

    async def get_thread(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Retorna un hilo por ID."""
        thread = await self.collection.find_one({"_id": ObjectId(thread_id)})
        if thread:
            thread["id"] = str(thread["_id"])
        return thread
