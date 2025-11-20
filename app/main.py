from fastapi import FastAPI
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.api.v1.endpoints.threads import router as threads_router
from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.moderation import router as moderation_router

app = FastAPI(title="Threads Service API")

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