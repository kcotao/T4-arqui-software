# test_items.py
from fastapi.testclient import TestClient
from app.main import app
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.api.v1.endpoints.threads import get_thread_repo

app.router.lifespan = None

async def fake_connect():
    return True

async def fake_close():
    return True

app.dependency_overrides[connect_to_mongo] = fake_connect
app.dependency_overrides[close_mongo_connection] = fake_close

class FakeRepo:
    async def get_channels(self, channel_id, thread_name, user_id):
        return {"id": "fake123","channel_id": channel_id ,"thread_name": thread_name, "user_id": user_id}

def fake_repo():
    return FakeRepo()

app.dependency_overrides[get_thread_repo] = fake_repo

client = TestClient(app)

def test_channel_success():
    response = client.get("/threads/channel/channels")
    
    assert response.status_code == 200 
