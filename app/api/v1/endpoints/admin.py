from fastapi import APIRouter, Depends
from app.db.mongodb import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()

@router.delete("/thread/{thread_id}", summary="Buscar cualquier thread según ID")
async def delete_thread(thread_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    await db.threads.delete_one({"_id": thread_id})
    return {"status": "deleted"}

@router.put("/thread/{thread_id}/classify", summary="Clasificar thread según ID")
async def classify_thread(thread_id: str, label: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    await db.threads.update_one({"_id": thread_id}, {"$set": {"label": label}})
    return {"status": "updated", "label": label}

@router.put("/thread/{thread_id}/deactivate", summary="Desactivar thread según ID")
async def deactivate_thread(thread_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    await db.threads.update_one({"_id": thread_id}, {"$set": {"active": False}})
    return {"status": "deactivated"}

@router.put("/thread/{thread_id}/reactivate", summary="Reactivar thread según ID")
async def reactivate_thread(thread_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    await db.threads.update_one({"_id": thread_id}, {"$set": {"active": True}})
    return {"status": "active"}

@router.get("/threads/count", summary="Cuenta la cantidad de threads totales en el sitio")
async def count_threads(db: AsyncIOMotorDatabase = Depends(get_database)):
    count = await db.threads.count_documents({})
    return {"count": count}

@router.get("/threads/count/{user_id}", summary="Cuenta las threads de un usuario específico")
async def count_threads_by_user(user_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    count = await db.threads.count_documents({"user_id": user_id})
    return {"user_id": user_id, "count": count}