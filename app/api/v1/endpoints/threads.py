from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongodb import get_database
from app.repositories.threads_repository import ThreadRepository
from app.models.threads import ThreadCreate, ThreadEdit
from datetime import datetime


router = APIRouter()

def get_thread_repo(db: AsyncIOMotorDatabase = Depends(get_database)):
    return ThreadRepository(db)

@router.get("/{thread_id}", summary="Buscar hilo por ID")
async def get_thread(thread_id: str, repo: ThreadRepository = Depends(get_thread_repo)):    
    doc = await repo.get_thread(thread_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Thread not found")
    return {"thread": doc}

@router.post("/", summary="Crear hilo")
async def create_thread(channel_id: str, thread_name: str, user_id: str, repo: ThreadRepository = Depends(get_thread_repo)):
    if not channel_id or not thread_name or not user_id:
        raise HTTPException(status_code=422, detail="Missing fields")
    return await repo.create_thread(channel_id, thread_name, user_id)


@router.delete("/{thread_id}", status_code=status.HTTP_204_NO_CONTENT,summary="Eliminar hilo")
async def delete_thread(thread_id: str, repo: ThreadRepository = Depends(get_thread_repo)):
    try:
        result = await repo.delete_thread(thread_id) 
        
    except Exception: 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID proporcionado no es un identificador válido."
        )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hilo con ID '{thread_id}' no encontrado."
        )
    return

@router.put("/{thread_id}/edit", summary="Editar hilo según id")
async def edit_thread(thread_id: str, update: ThreadEdit, repo: ThreadRepository = Depends(get_thread_repo)):
    ok = await repo.edit_thread(thread_id, update.dict(exclude_none=True))
    return {"success": ok}

@router.get("/mine/{user_id}", summary="Revisar hilos creados según ID de usuario")
async def get_my_threads(user_id: str, repo: ThreadRepository = Depends(get_thread_repo)):
    return await repo.get_user_threads(user_id)