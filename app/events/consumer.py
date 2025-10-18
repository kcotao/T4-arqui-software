import json, asyncio, aio_pika
from aiormq import AMQPConnectionError
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import delete
from ..models import Channel
from ..config import settings

class ChannelEventConsumer:
    def __init__(self, session_factory):
        self._sf = session_factory
        self._conn = None
        self._channel = None

    async def start(self, retries=20, base_delay=0.5):
        if not settings.enable_events: 
            return
        last = None
        for attempt in range(retries):
            try:
                self._conn = await aio_pika.connect_robust(settings.rabbitmq_url)
                self._channel = await self._conn.channel()
                ex = await self._channel.declare_exchange(
                    settings.event_exchange, aio_pika.ExchangeType.TOPIC, durable=True
                )
                q = await self._channel.declare_queue(settings.channel_event_queue, durable=True)
                await q.bind(ex, routing_key="channel.*")
                await q.consume(self._on_message)
                return
            except (AMQPConnectionError, ConnectionError) as e:
                last = e
                await asyncio.sleep(min(5.0, base_delay * (2**attempt)))
        if last: raise last

    async def _on_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            payload = json.loads(message.body.decode("utf-8"))
            data = payload.get("data", {})
            name = payload.get("event_name", "")
            async with self._sf() as s:  # type: AsyncSession
                if name in ("channel.created","channel.updated"):
                    ch = Channel(id=data["id"], name=data["name"], is_active=data.get("is_active", True))
                    await s.merge(ch); await s.commit()
                elif name == "channel.deleted":
                    await s.exec(delete(Channel).where(Channel.id == data["id"]))
                    await s.commit()
