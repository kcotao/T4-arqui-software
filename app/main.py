from fastapi import FastAPI,  Request
from contextlib import asynccontextmanager
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints.threads import router as threads_router
from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.moderation import router as moderation_router
from app.api.v1.endpoints.message import router as message_router
from app.api.v1.endpoints.channels import router as channel_router
from app.api.v1.events.publisher import EventPublisher
from app.api.v1.events.consumer import ChannelEventConsumer
from app.core.config import settings
from bson import ObjectId


publisher = EventPublisher()
consumer = ChannelEventConsumer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- INICIO ---
    print("Iniciando conexión a MongoDB...")
    # 2. Aquí usamos AWAIT correctamente
    await connect_to_mongo() 
    
    print("Iniciando Consumidor de RabbitMQ...")
    # 3. Arrancamos el consumidor como tarea de fondo
    import asyncio
    asyncio.create_task(consumer.start())
    
    yield
    # --- APAGADO ---
    print("Apagando servicios...")
    await close_mongo_connection()

json_encoders_config = {
    ObjectId: str
}

app = FastAPI(lifespan=lifespan, 
              title="Threads Service",
              root_path="/threads", 
              docs_url="/docs",
              openapi_url="/openapi.json",
              json_encoders=json_encoders_config)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins or ["http://127.0.0.1:3000", "http://localhost:3000","http://localhost:8000", "http://127.0.0.1:3000" ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_accept(request: Request, call_next):
    print("Accept:", request.headers.get("accept"))
    return await call_next(request)


@app.on_event("startup")
async def startup():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown():
    await close_mongo_connection()

# Rutas organizadas por módulos
app.include_router(threads_router, prefix="/threads", tags=["Threads"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(moderation_router, prefix="/moderation", tags=["Moderación"])
app.include_router(message_router, prefix="/message", tags=["Mensaje en Thread"])
app.include_router(channel_router, prefix="/channel", tags=["Canales"])