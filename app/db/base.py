from motor.motor_asyncio import AsyncIOMotorDatabase

class BaseRepository:
    def __init__(self, db: AsyncIOMotorDatabase, collection: str):
        self.db = db
        self.collection = db[collection]

    async def create(self, data: dict) -> str:
        result = await self.collection.insert_one(data)
        return str(result.inserted_id)

    async def find_all(self):
        docs = await self.collection.find().to_list(100)
        return docs