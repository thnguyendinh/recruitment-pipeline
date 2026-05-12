"""
Fake data generator — bám theo ngày cuối của tracking.csv (2022-07-27)
Mỗi phút thực tế = 1 giờ trong fake timeline
→ Dashboard sẽ thấy data tăng dần từ 2022-07-27 trở đi
"""
import random
from datetime import datetime, timedelta
from pymongo import MongoClient

client = MongoClient("mongodb://admin:admin123@localhost:27017/recruitment?authSource=admin")
collection = client["recruitment"]["tracking"]

# Ngày cuối của tracking.csv
BASE_DATE = datetime(2022, 7, 27, 0, 0, 0)

# Tính fake timestamp:
# Lấy số phút đã chạy kể từ lần đầu tiên (dựa vào count fake docs)
# Mỗi phút thực = 1 giờ fake → mỗi lần chạy tăng thêm 1 giờ
fake_count = collection.count_documents({"source": "fake_generator"})
hours_offset = fake_count // 35  # ~35 events/lần, mỗi lần = 1 giờ
fake_now = BASE_DATE + timedelta(hours=hours_offset)

JOB_IDS       = [101, 102, 103, 104, 105, 106, 107]
PUBLISHER_IDS = [1, 2, 3, 4, 5]
CAMPAIGN_IDS  = [201, 202, 203, 204]
GROUP_IDS     = [301, 302, 303]

# Tỷ lệ giống thực tế: 80% click, 10% conversion, 5% qualified, 5% unqualified
EVENT_TYPES = (
    ["click"] * 8 +
    ["conversion"] * 2 +
    ["qualified"] * 1 +
    ["unqualified"] * 1
)

def generate_event():
    # Thêm random giây trong giờ hiện tại để data trải đều
    random_seconds = random.randint(0, 3599)
    ts = fake_now + timedelta(seconds=random_seconds)
    return {
        "job_id":       random.choice(JOB_IDS),
        "publisher_id": random.choice(PUBLISHER_IDS),
        "campaign_id":  random.choice(CAMPAIGN_IDS),
        "group_id":     random.choice(GROUP_IDS),
        "custom_track": random.choice(EVENT_TYPES),
        "bid":          round(random.uniform(0.5, 5.0), 2),
        "ts":           ts.strftime("%Y-%m-%d %H:%M:%S.000"),
        "create_time":  str(ts.timestamp()),
        "source":       "fake_generator"
    }

n = random.randint(30, 50)
events = [generate_event() for _ in range(n)]
collection.insert_many(events)

print(f"[{datetime.now().strftime('%H:%M:%S')}] Fake time: {fake_now.strftime('%Y-%m-%d %H:00')} | Inserted {n} events")
client.close()
