from bson import ObjectId

class ModerationRepository:
    def __init__(self, db):
        self.collection = db["threads"]
        self.hidden = db["hidden_threads"]
        self.reports = db["thread_reports"]

    async def hide_thread(self, thread_id: str, user_id: str):
        await self.hidden.update_one(
            {"thread_id": thread_id},
            {"$set": {"hidden_by": user_id}},
            upsert=True
        )
        return True

    async def unhide_thread(self, thread_id: str):
        await self.hidden.delete_one({"thread_id": thread_id})
        return True

    async def report_thread(self, thread_id: str, reason: str, user_id: str):
        await self.reports.insert_one({
            "thread_id": thread_id,
            "reason": reason,
            "reported_by": user_id
        })
        return True

    async def get_hidden_threads(self, user_id: str):
        cursor = self.hidden.find({"hidden_by": user_id})
        hidden_ids = [doc["thread_id"] async for doc in cursor]

        return self.collection.find({"_id": {"$in": [ObjectId(x) for x in hidden_ids]}})
