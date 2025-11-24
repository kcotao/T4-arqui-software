from fastapi import APIRouter
from app.services.message_services import Message_Client
from app.models.consumer import Channel

router = APIRouter()

@router.post("/message-on-thread")
async def mi_funcion(thread_id: str, user_id: str, content: str):
    
    resultado = await Message_Client.post_message_on_thread(
        thread_id=thread_id, 
        user_id=user_id, 
        content=content
    )
    
    return {"status": "ok", "resultado_externo": resultado}