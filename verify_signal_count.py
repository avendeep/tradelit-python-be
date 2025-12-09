
import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append("c:/Users/prade/Desktop/TradeLit/tradeLit_app")

from app.services.trade_decision_centre import trade_decision_centre
from app.schemas.trading_bot import OIAnalysisResult, StrikeOIAnalysis
from app.db.mongodb import MongoDB
from app.core.config import settings

async def main():
    print("Connecting to DB...")
    await MongoDB.connect_db()

    # Simulate an analysis result that leads to BULLISH PUSH
    # Logic: put_change > 0 and call_change < 0 -> BULLISH PUSH
    # Need 5 strikes.
    
    strikes = []
    # ATM-2, ATM-1, ATM, ATM+1, ATM+2
    strike_prices = [100, 105, 110, 115, 120]
    atm = 110.0
    
    for sp in strike_prices:
        strikes.append(StrikeOIAnalysis(
            strike_price=sp,
            call_oi_change=-1000,
            put_oi_change=1000,
            call_oi=5000,
            put_oi=6000
        ))

    analysis = OIAnalysisResult(
        bot_id="test_bot",
        instrument_key="TEST_INSTRUMENT",
        expiry_date="2024-12-31",
        timestamp=datetime.now(),
        atm_strike=atm,
        strikes_analyzed=strikes,
        pcr_oi=1.5, # > 1 for Bullish
        signal="BUY",
        total_call_oi_change=-5000,
        total_put_oi_change=5000
    )

    print("Logging analysis (expecting BULLISH PUSH count increment)...")
    await trade_decision_centre.log_analysis(analysis)
    
    # Verify DB
    db = MongoDB.get_database()
    today_str = datetime.now().strftime("%Y-%m-%d")
    doc = await db["daily_signal_counts"].find_one({"date": today_str, "instrument_key": "TEST_INSTRUMENT"})
    
    print("\n--- Verification Result ---")
    if doc:
        print(f"Document found for {today_str}: {doc}")
        if doc.get("bullish_push_count") >= 1:
            print("✅ SUCCESS: Bullish push count incremented.")
        else:
            print("❌ FAILURE: Bullish push count NOT incremented.")
    else:
        print("❌ FAILURE: Document not found.")

    await MongoDB.close_db()

if __name__ == "__main__":
    asyncio.run(main())
