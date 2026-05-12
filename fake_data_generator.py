#!/usr/bin/env python3
import random
import time
from datetime import datetime
from pymongo import MongoClient

# Kết nối MongoDB
client = MongoClient("mongodb://admin:admin123@localhost:27017/")
db = client.recruitment
collection = db.tracking

# Các giá trị có thể có
JOB_IDS = [1531, 1527, 1530, 98, 187, 258, 2, 188, 273, 1529]
CAMPAIGN_IDS = [222, 1, 48, 93, 4, 57]
GROUP_IDS = [30, 10, 25, 41, 48]
PUBLISHER_IDS = [1, 3, 9, 22]
CUSTOM_TRACKS = ["click", "conversion", "qualified", "unqualified"]
BID_RANGE = (0, 5)

def generate_log():
    """Tạo một log giả với timestamp hiện tại"""
    return {
        "ts": datetime.now(),
        "job_id": random.choice(JOB_IDS),
        "custom_track": random.choice(CUSTOM_TRACKS),
        "bid": random.randint(*BID_RANGE),
        "campaign_id": random.choice(CAMPAIGN_IDS),
        "group_id": random.choice(GROUP_IDS),
        "publisher_id": random.choice(PUBLISHER_IDS),
        # Các field khác có thể để null hoặc default
        "create_time": datetime.now(),
        "bn": "Chrome",
        "cd": 24,
        "de": "UTF-8",
        "dl": "http://example.com",
        "dt": "CandidatePortal",
        "ed": None,
        "ev": 1,
        "id": f"fake-{random.randint(1000,9999)}",
        "md": True,
        "rl": None,
        "sr": "1366x768",
        "tz": -420,
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "uid": f"user-{random.randint(1,100)}",
        "utm_campaign": None,
        "utm_content": None,
        "utm_medium": None,
        "utm_source": None,
        "utm_term": None,
        "v": 1,
        "vp": "1366x768"
    }

def insert_batch(batch_size=10):
    """Chèn batch_size logs vào MongoDB"""
    logs = [generate_log() for _ in range(batch_size)]
    result = collection.insert_many(logs)
    print(f"[{datetime.now()}] Inserted {len(result.inserted_ids)} logs")
    return len(result.inserted_ids)

if __name__ == "__main__":
    insert_batch(batch_size=random.randint(5, 15))
