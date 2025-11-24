import json, uuid, asyncio
from datetime import datetime, timezone
import aio_pika
from aiormq import AMQPConnectionError
from app.core.config import settings

class EventPublisher:
    def __init__(self):
        self._conn = None
        self._channel = None
        self._exchange = None

    async def connect(self, retries=20, base_delay=0.5):
        if not settings.enable_events: 
            return
        last = None
        for attempt in range(retries):
            try:
                self._conn = await aio_pika.connect_robust(settings.rabbitmq_url)
                self._channel = await self._conn.channel()
                self._exchange = await self._channel.declare_exchange(
                    settings.event_exchange, aio_pika.ExchangeType.TOPIC, durable=True
                )
                return
            except (AMQPConnectionError, ConnectionError) as e:
                last = e
                await asyncio.sleep(min(5.0, base_delay * (2**attempt)))
        if last: raise last

    async def close(self):
        if self._conn:
            await self._conn.close()

    async def publish(self, routing_key: str, name: str, data: dict):
        if not settings.enable_events:
            return
        if not self._exchange:
            await self.connect()
        envelope = {
            "event_name": name,
            "version": settings.event_version,
            "occurred_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "producer": settings.service_name,
            "trace_id": str(uuid.uuid4()),
            "data": data,
        }
        await self._exchange.publish(
            aio_pika.Message(
                body=json.dumps(envelope).encode("utf-8"),
                content_type="application/json",
                headers={"X-Event-Version": settings.event_version},
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=routing_key,
        )