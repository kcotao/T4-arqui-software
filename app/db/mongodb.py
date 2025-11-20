from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

MONGO_URL = "mongodb://localhost:27017"
MONGO_DB = "threads_db"

class MongoDB:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None

mongodb = MongoDB()

async def connect_to_mongo():
    if mongodb.client is None:
        mongodb.client = AsyncIOMotorClient(MONGO_URL)
        mongodb.db = mongodb.client[MONGO_DB]

async def close_mongo_connection():
    if mongodb.client:
        mongodb.client.close()
        mongodb.client = None
        mongodb.db = None

async def get_database() -> AsyncIOMotorDatabase:
    if mongodb.db is None:
        await connect_to_mongo()
    return mongodb.db