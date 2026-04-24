import json
from pymongo import MongoClient
import os
import uuid6
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["profile_db"]
collection = db["profiles"]

with open("data.json") as f:
    data = json.load(f)["profiles"]

for item in data:
    item["name"] = item["name"].lower()
    item["id"] = str(uuid6.uuid7())
    item["created_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    collection.update_one(
        {"name": item["name"]},
        {"$set": item},
        upsert=True
    )

print("Seeding complete ✅")