import json, asyncio, aio_pika
from aiormq import AMQPConnectionError
import uuid
from beanie import PydanticObjectId
from app.models.consumer import Channel 
from app.core.config import settings

class ChannelEventConsumer:
    def __init__(self):
        self._conn = None
        self._channel = None

    async def start(self, retries=20, base_delay=0.5):
        
        if not settings.enable_events: 
            return

        last = None
        for attempt in range(retries):
            try:
                print(f"[CONSUMER] Conectando... (Intento {attempt+1})")
                self._conn = await aio_pika.connect_robust(settings.rabbitmq_url)
                self._channel = await self._conn.channel()
                

                ex = await self._channel.declare_exchange(
                    settings.event_exchange, aio_pika.ExchangeType.TOPIC, durable=True
                )
                
                q = await self._channel.declare_queue(
                    settings.channel_event_queue, 
                    durable=True
                )


                # OJO: Aquí usé '#' porque en tu foto vimos que el otro equipo usaba '#'
                await q.bind(ex, routing_key="channelService.#") 
                await q.consume(self._on_message)
                
                print("[CONSUMER] ¡Todo listo y escuchando!")
                return

            except Exception as e:
                last = e
                print(f"[ERROR] Fallo en paso de configuración: {e}")
                print("Reintentando en 5s...")
                await asyncio.sleep(5)
        
        if last: raise last

    async def _on_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            
            payload = json.loads(message.body.decode("utf-8"))
            routing_key = message.routing_key
            data = payload.get("data", {}) or payload
            ext_id_str = data.get("_id") or data.get("id") or data.get("channel_id")
            ext_name = payload.get("name", "Sin Nombre")
            ext_active = payload.get("is_active", True)
            
            if not ext_id_str:
                print("Mensaje ignorado: No tiene channel_id")
                return

            try:
                channel_oid = PydanticObjectId(ext_id_str)
            except Exception:
                print(f"ID inválido, no es ObjectId: {ext_id_str}")
            

            print(f" Procesando: {routing_key} | ID: {channel_oid}")

            if "created" in routing_key or "updated" in routing_key:
                    existing_channel = await Channel.get(channel_oid)
                    
                    if existing_channel:
                        # === CASO ACTUALIZAR ===
                        existing_channel.name = ext_name
                        existing_channel.is_active = ext_active
                        await existing_channel.save() 
                        print(f"✅ [UPDATE] Canal actualizado en Mongo: {ext_name}")
                        
                    else:
                        # === CASO CREAR ===
                        new_channel = Channel(
                            id=channel_oid,
                            name=ext_name,
                            is_active=ext_active
                        )
                        await new_channel.insert()
                        print(f"Canal nuevo guardado en Mongo: {ext_name}")

                # BORRAR
            elif "deleted" in routing_key:
                channel_to_delete = await Channel.get(channel_oid)
                if channel_to_delete:
                        
                    await channel_to_delete.delete()
                    print(f"Canal eliminado de Mongo.")