import httpx
from fastapi import HTTPException
from app.core.config import settings

class MessageClient:
    def __init__(self):
        self.base_url = settings.message_url_services

    async def post_message_on_thread(self, user_id: str,thread_id: str, content: str) -> dict | None:
        url = f"{self.base_url}/threads/{thread_id}/message"
        
        header = {
            "X-User-Id": user_id,
            "Content-Type": "application/json"
        }

        payload = {
            "content": content,
            "type": "text",
            "path": "[]"
        }

        print("Enviando Mensaje... query:{url} con user {user_id}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url,
                                             headers=header,
                                             json=payload,
                                             timeout=5.0)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None
                else:
                    print(f"Error del servicio usuarios: {response.text}")
                    return None
                    
        except httpx.RequestError as e:
            print(f" No se pudo conectar con el servicio de usuarios: {e}")
            return None

# Instancia lista para usar
Message_Client = MessageClient()