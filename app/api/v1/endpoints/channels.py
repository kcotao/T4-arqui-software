from fastapi import APIRouter, Depends
from typing import List
from app.models.consumer import Channel 
from app.models.threads import ThreadBase
from app.repositories.threads_repository import ThreadRepository
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongodb import get_database


router = APIRouter()

def get_thread_repo(db: AsyncIOMotorDatabase = Depends(get_database)):
    return ThreadRepository(db)

@router.get("/channels",summary= "Obtener canales disponibles", response_model=List[Channel])
async def get_channels():
    """
    Obtiene la lista de canales disponibles (desde la réplica local).
    """
    channels = await Channel.find_all().to_list()
    return channels

@router.get("/get_threads", summary= "Devuelve todos los hilos asociados a un canal",response_model=List[ThreadBase])
async def get_threads(channel_id: str, repo: ThreadRepository = Depends(get_thread_repo)):
    return await repo.get_threads(channel_id)