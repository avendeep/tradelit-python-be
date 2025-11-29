import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.mongodb import MongoDB
from app.services.analysis_service import analysis_service
from app.core.config import settings

async def verify_eod_analysis():
    print("🚀 Starting EOD Analysis Verification...")
    
    await MongoDB.connect_db()
    
    instrument_key = "TEST_INSTRUMENT"
    date = "2025-01-01"
    doc_id = f"{instrument_key}_{date}"
    
    # 1. Insert dummy candle data
    print("1️⃣ Inserting dummy candle data...")
    candle_collection = MongoDB.get_collection("intraday_candles")
    
    # Create dummy candles
    # Candle 1: Bullish (Close > Open) -> Delta should be positive
    # Vol: 100, Open: 100, Close: 110, High: 110, Low: 100. Range: 10. Delta = 100 * (10/10) = 100
    
    # Candle 2: Bearish (Close < Open) -> Delta should be negative
    # Vol: 200, Open: 110, Close: 100, High: 110, Low: 100. Range: 10. Delta = 200 * (-10/10) = -200
    
    # Candle 3: Doji (Close = Open) -> Delta should be 0
    # Vol: 50, Open: 100, Close: 100, High: 105, Low: 95. Range: 10. Delta = 50 * (0/10) = 0
    
    dummy_candles = [
        {"timestamp": datetime(2025, 1, 1, 9, 15), "open": 100, "high": 110, "low": 100, "close": 110, "volume": 100},
        {"timestamp": datetime(2025, 1, 1, 9, 30), "open": 110, "high": 110, "low": 100, "close": 100, "volume": 200},
        {"timestamp": datetime(2025, 1, 1, 9, 45), "open": 100, "high": 105, "low": 95, "close": 100, "volume": 50},
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
    print("✅ Dummy data inserted.")
    
    # 2. Run Analysis
    print("2️⃣ Running AnalysisService.calculate_daily_delta...")
    delta = await analysis_service.calculate_daily_delta(instrument_key, date)
    
    print(f"📊 Calculated Delta: {delta}")
    
    # Expected Delta: 100 - 200 + 0 = -100
    expected_delta = -100.0
    
    if delta == expected_delta:
        print("✅ Verification PASSED! Delta matches expected value.")
    else:
        print(f"❌ Verification FAILED! Expected {expected_delta}, got {delta}")
        
    # 3. Check Database Storage
    print("3️⃣ Checking database storage...")
    analysis_collection = MongoDB.get_collection("eod_analysis")
    stored_doc = await analysis_collection.find_one({"_id": doc_id})
    
    if stored_doc and stored_doc["daily_cumulative_delta"] == expected_delta:
        print("✅ Database storage verified.")
    else:
        print("❌ Database storage verification failed.")
        
    # Cleanup
    await candle_collection.delete_one({"_id": doc_id})
    await analysis_collection.delete_one({"_id": doc_id})
    await MongoDB.close_db()
    print("🧹 Cleanup done.")

if __name__ == "__main__":
    asyncio.run(verify_eod_analysis())
