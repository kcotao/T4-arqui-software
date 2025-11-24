from fastapi import APIRouter
from motor.motor_asyncio import AsyncIOMotorDatabase
router = APIRouter()

@router.get("/")
async def healthcheck():
    return {"status": "ok"}