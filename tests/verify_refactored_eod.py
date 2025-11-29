import urllib.request
import json
import time
import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.db.mongodb import MongoDB

BASE_URL = "http://localhost:8000/api/v1/analysis"

async def setup_dummy_data():
    print("0️⃣ Setting up dummy candle data...")
    await MongoDB.connect_db()
    candle_collection = MongoDB.get_collection("intraday_candles")
    
    instrument_key = "REFACTOR_TEST"
    date = "2025-02-01"
    doc_id = f"{instrument_key}_{date}"
    
    dummy_candles = [
        {"timestamp": datetime(2025, 2, 1, 9, 15), "open": 100, "high": 110, "low": 100, "close": 110, "volume": 100},
    ]
    
    await candle_collection.replace_one(
        {"_id": doc_id},
        {
            "_id": doc_id,
            "instrument_key": instrument_key,
            "date": date,
            "interval": "15minute",
            "candles": dummy_candles,
            "updated_at": datetime.now()
        },
        upsert=True
    )
    await MongoDB.close_db()
    print("✅ Dummy data setup complete.")

def test_refactored_api():
    print("🚀 Starting Refactored API Verification...")
    
    # 1. Set Config
    print("1️⃣ Setting Configuration...")
    data = {
        "instrument_key": "REFACTOR_TEST",
        "date": "2025-02-01"
    }
    req = urllib.request.Request(
        f"{BASE_URL}/config",
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print("✅ Config set successfully")
            else:
                print(f"❌ Config set failed: {response.status}")
                return
    except Exception as e:
        print(f"❌ Config set failed: {e}")
        return

    # 2. Call Delta API (No params)
    print("2️⃣ Calling POST /eod/delta (No params)...")
    req = urllib.request.Request(
        f"{BASE_URL}/eod/delta",
        data=b"", # Empty body
        headers={'Content-Type': 'application/json'}, # Content-Length: 0
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                res_body = json.loads(response.read().decode('utf-8'))
                print(f"   Response: {res_body}")
                if res_body['instrument_key'] == "REFACTOR_TEST" and res_body['date'] == "2025-02-01":
                     print("✅ Verification passed: Used configured values.")
                else:
                     print("❌ Verification failed: Returned wrong values.")
            else:
                print(f"❌ API call failed with status {response.status}")
    except Exception as e:
        print(f"❌ API call failed: {e}")

if __name__ == "__main__":
    # Run async setup first
    asyncio.run(setup_dummy_data())
    # Then run sync tests
    test_refactored_api()
