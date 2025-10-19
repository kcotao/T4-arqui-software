from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .db import init_db, async_session
from .config import settings
from .events.publisher import EventPublisher
from .events.consumer import ChannelEventConsumer
from .routers import threads as threads_router
from .routers import dev as dev_router

app = FastAPI(title="Threads Service", version="1.0.0")
publisher = EventPublisher()
consumer = ChannelEventConsumer(async_session)

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

@app.get("/healthz")
async def health(): return {"status":"ok"}

@app.on_event("startup")
async def on_startup():
    await init_db()
    await publisher.connect()
    await consumer.start()

@app.on_event("shutdown")
async def on_shutdown():
    await publisher.close()

app.include_router(threads_router.router, prefix="/v1", tags=["threads"])
app.include_router(dev_router.router, prefix="/v1/dev", tags=["dev"])  # solo en desarrollo