from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongodb import get_database
from app.repositories.moderation_repository import ModerationRepository
from app.models.threads import ThreadReport, ThreadHide

router = APIRouter()

def get_mod_repo(db: AsyncIOMotorDatabase = Depends(get_database)):
    return ModerationRepository(db)

@router.put("/hide/{thread_id}", summary="Ocultar Thread por ID")
async def hide_thread(thread_id: str, payload: ThreadHide, repo: ModerationRepository = Depends(get_mod_repo)):
    return await repo.hide_thread(thread_id, payload.hidden_by)

@router.put("/unhide/{thread_id}", summary="Volver a mostrar thread oculta")
async def unhide_thread(thread_id: str, repo: ModerationRepository = Depends(get_mod_repo)):
    return await repo.unhide_thread(thread_id)

@router.put("/report/{thread_id}", summary= "Reportar thread según ID")
async def report_thread(thread_id: str, payload: ThreadReport, repo: ModerationRepository = Depends(get_mod_repo)):
    return await repo.report_thread(thread_id, payload.reason, payload.reported_by)

@router.get("/hidden/{user_id}", summary= "Mostrar todos los hilos ocultos")
async def get_hidden_threads(user_id: str, repo: ModerationRepository = Depends(get_mod_repo)):
    cursor = await repo.get_hidden_threads(user_id)
    return [doc async for doc in cursor]
