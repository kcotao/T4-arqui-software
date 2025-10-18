import os

class Settings:
    database_url = os.getenv("DATABASE_URL", "")
    rabbitmq_url = os.getenv("RABBITMQ_URL", "")
    event_exchange = os.getenv("EVENT_EXCHANGE", "platform.events")
    event_version = int(os.getenv("EVENT_VERSION", "1"))
    channel_event_queue = os.getenv("CHANNEL_EVENT_QUEUE", "threads.channel.events")
    service_name = os.getenv("SERVICE_NAME", "threads")
    enable_events = os.getenv("ENABLE_EVENTS", "true").lower() == "true"
    allowed_origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS","").split(",") if o.strip()]

settings = Settings()
