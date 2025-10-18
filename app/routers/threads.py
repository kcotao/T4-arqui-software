from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Response
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from ..db import async_session
from ..models import Thread, Channel, ThreadStatus
from ..schemas import ThreadCreate, ThreadUpdate, ThreadOut
from ..events.publisher import EventPublisher
from fastapi.encoders import jsonable_encoder
import logging

log = logging.getLogger(__name__)

VENDOR = "application/vnd.threads.v1+json"

router = APIRouter()

async def get_db() -> AsyncSession:
    async with async_session() as s:
        yield s

async def get_publisher() -> EventPublisher:
    from ..main import publisher
    return publisher

def ensure_accept(accept: Optional[str]):
    # Relajado para que Swagger (application/json) tambiÃ©n pase
    if not accept:
        return
    a = accept.lower()
    if (VENDOR in a) or ("application/json" in a) or ("*/*" in a):
        return
    raise HTTPException(status_code=406, detail="Not Acceptable")

async def safe_publish(publisher: EventPublisher, event: str, routing_key: str, data):
    """Publica sin romper la request si hay error y serializa datetimes a ISO."""
    try:
        payload = jsonable_encoder(data)
        await publisher.publish(event, routing_key, payload)
    except Exception:
        log.exception("publish failed for %s", event)

@router.post("", response_model=ThreadOut, status_code=201)
async def create_thread(
    payload: ThreadCreate,
    response: Response,
    db: AsyncSession = Depends(get_db),
    publisher: EventPublisher = Depends(get_publisher),
    accept: Optional[str] = Header(default=None),
):
    ensure_accept(accept)
    ch = await db.get(Channel, payload.channel_id)
    if not ch or not ch.is_active:
        raise HTTPException(status_code=404, detail="Channel not found or inactive")

    th = Thread(
        channel_id=payload.channel_id,
        title=payload.title,
        created_by=payload.created_by,
        meta=payload.meta,
    )
    db.add(th)
    await db.commit()
    await db.refresh(th)

    out = ThreadOut.model_validate(th, from_attributes=True)
    await safe_publish(publisher, "thread.created", "thread.created", out)
    return out

@router.get("", response_model=List[ThreadOut])
async def list_threads(
    channel_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    accept: Optional[str] = Header(default=None),
):
    ensure_accept(accept)
    stmt = select(Thread).where(Thread.deleted_at.is_(None))
    if channel_id:
        stmt = stmt.where(Thread.channel_id == channel_id)
    rows = (await db.exec(stmt.order_by(Thread.created_at.desc()))).all()
    return [ThreadOut.model_validate(r, from_attributes=True) for r in rows]

@router.get("/{thread_id}", response_model=ThreadOut)
async def get_thread(
    thread_id: str,
    db: AsyncSession = Depends(get_db),
    accept: Optional[str] = Header(default=None),
):
    ensure_accept(accept)
    th = await db.get(Thread, thread_id)
    if not th or th.deleted_at:
        raise HTTPException(status_code=404, detail="Thread not found")
    return ThreadOut.model_validate(th, from_attributes=True)

@router.patch("/{thread_id}", response_model=ThreadOut)
async def update_thread(
    thread_id: str,
    payload: ThreadUpdate,
    db: AsyncSession = Depends(get_db),
    publisher: EventPublisher = Depends(get_publisher),
    accept: Optional[str] = Header(default=None),
):
    ensure_accept(accept)
    th = await db.get(Thread, thread_id)
    if not th or th.deleted_at:
        raise HTTPException(status_code=404, detail="Thread not found")

    changed = False
    if payload.title is not None:
        th.title = payload.title
        changed = True
    if payload.status is not None:
        th.status = payload.status
        changed = True
    if payload.meta is not None:
        th.meta = payload.meta
        changed = True

    if changed:
        th.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(th)
        out = ThreadOut.model_validate(th, from_attributes=True)
        await safe_publish(publisher, "thread.updated", "thread.updated", out)
        return out

    return ThreadOut.model_validate(th, from_attributes=True)

@router.post("/{thread_id}:archive", response_model=ThreadOut)
async def archive_thread(
    thread_id: str,
    db: AsyncSession = Depends(get_db),
    publisher: EventPublisher = Depends(get_publisher),
    accept: Optional[str] = Header(default=None),
):
    ensure_accept(accept)
    th = await db.get(Thread, thread_id)
    if not th or th.deleted_at:
        raise HTTPException(status_code=404, detail="Thread not found")

    th.status = ThreadStatus.ARCHIVED
    th.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(th)

    out = ThreadOut.model_validate(th, from_attributes=True)
    await safe_publish(publisher, "thread.archived", "thread.archived", out)
    return out

@router.delete("/{thread_id}", status_code=204)
async def delete_thread(
    thread_id: str,
    db: AsyncSession = Depends(get_db),
    publisher: EventPublisher = Depends(get_publisher),
    accept: Optional[str] = Header(default=None),
):
    ensure_accept(accept)
    th = await db.get(Thread, thread_id)
    if not th or th.deleted_at:
        raise HTTPException(status_code=404, detail="Thread not found")

    th.deleted_at = datetime.utcnow()
    th.updated_at = datetime.utcnow()
    await db.commit()

    await safe_publish(
        publisher,
        "thread.deleted",
        "thread.deleted",
        {"id": thread_id, "channel_id": th.channel_id},
    )
    return Response(status_code=204)