from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie
from app.core.config import settings 
# IMPORTANTE: Importa aquí TODOS tus modelos
from app.models.consumer import Channel 

class MongoDB:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None

mongodb = MongoDB()

async def connect_to_mongo():
    if mongodb.client is None:
        # 1. Usamos settings.database_url para que funcione en Docker y Local
        # (Si usas "localhost" harcodeado, fallará en Docker)
        mongodb.client = AsyncIOMotorClient(settings.database_url)
        
        # 2. Seleccionamos la base de datos
        mongodb.db = mongodb.client[settings.mongo_db_name]
        
        # 3. ¡ESTO ES LO QUE FALTABA! Inicializar Beanie
        print("Inicializando Beanie...")
        await init_beanie(
            database=mongodb.db,
            document_models=[Channel]  # <--- Aquí registras tus clases
        )
        print("MongoDB y Beanie conectados exitosamente")

async def close_mongo_connection():
    if mongodb.client:
        mongodb.client.close()
        mongodb.client = None
        mongodb.db = None
        print("🛑 Conexión a Mongo cerrada")

async def get_database() -> AsyncIOMotorDatabase:
    if mongodb.db is None:
        await connect_to_mongo()
    return mongodb.db