from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Any, List

class BaseRepository:
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str):
        self.db = db
        self.collection = db[collection_name]

    async def insert_one(self, document: dict) -> str:
        res = await self.collection.insert_one(document)
        return str(res.inserted_id)

    async def find_one(self, query: dict) -> dict | None:
        return await self.collection.find_one(query)

    async def find_many(self, query: dict, sort: list = None, limit: int = 0) -> List[dict]:
        cursor = self.collection.find(query)
        if sort:
            cursor = cursor.sort(sort)
        if limit:
            return await cursor.to_list(limit)
        return await cursor.to_list(100)
    
    async def update_one(self, query: dict, update: dict) -> bool:
        res = await self.collection.update_one(query, update)
        return res.modified_count > 0
