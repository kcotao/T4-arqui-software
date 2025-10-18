from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, select
from sqlmodel.ext.asyncio.session import AsyncSession

from .db import async_engine, async_session

VENDOR = "application/vnd.messages.v1+json"

app = FastAPI(title="Messages Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
    allow_origins=["http://localhost:3000","http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers["*"],
)

class Message(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    thread_id: UUID = Field(index=True)
    author: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MessageCreate(BaseModel):
    thread_id: UUID
    author: str
    content: str

class MessageOut(BaseModel):
    id: UUID
    thread_id: UUID
    author: str
    content: str
    created_at: datetime

async def get_db():
    async with async_session() as s:
        yield s

def ensure_accept(accept: Optional[str]):
    # MantÃ©n esto permisivo para que /docs funcione sin pelear
    if not accept:
        return
    a = accept.lower()
    if (VENDOR in a) or ("application/json" in a) or ("*/*" in a):
        return
    raise HTTPException(status_code=406, detail="Not Acceptable")

@app.on_event("startup")
async def on_startup():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

@app.get("/healthz")
async def health():
    return {"ok": True}

@app.get("/v1/messages", response_model=List[MessageOut])
async def list_messages(
    thread_id: UUID,
    db: AsyncSession = Depends(get_db),
    accept: Optional[str] = Header(default=None),
):
    ensure_accept(accept)
    stmt = select(Message).where(Message.thread_id == thread_id).order_by(Message.created_at.asc())
    rows = (await db.exec(stmt)).all()
    return [MessageOut.model_validate(r, from_attributes=True) for r in rows]

@app.post("/v1/messages", response_model=MessageOut, status_code=201)
async def create_message(
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    accept: Optional[str] = Header(default=None),
):
    ensure_accept(accept)
    msg = Message(**payload.model_dump())
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    # Si luego publicas eventos, usa jsonable_encoder(msg) para serializar datetimes
    _ = jsonable_encoder(msg)  # no-op, solo ejemplo
    return MessageOut.model_validate(msg, from_attributes=True)
