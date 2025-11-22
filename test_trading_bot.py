"""
Test script for Trading Bot functionality
Tests bot activation, analysis, and deactivation
"""

import asyncio
import sys
from datetime import datetime, timedelta

# Add app directory to path
sys.path.insert(0, ".")

from app.db.mongodb import MongoDB
from app.services.trading_bot import trading_bot_service
from app.services.upstox_service import upstox_service


async def test_trading_bot():
    """Test trading bot functionality"""

    print("=" * 80)
    print("🤖 TRADING BOT TEST")
    print("=" * 80)
    print()

    # Connect to MongoDB
    print("📦 Connecting to MongoDB...")
    await MongoDB.connect_db()
    print("✅ Connected to MongoDB")
    print()

    # Load Upstox token
    print("🔐 Loading Upstox token...")
    token_loaded = await upstox_service.load_token_from_db()
    if not token_loaded or not upstox_service.is_token_valid():
        print("❌ Upstox token not valid. Please authenticate first.")
        print("Run: python test_upstox_auth.py")
        await MongoDB.close_db()
        return
    print("✅ Upstox token loaded and valid")
    print()

    # Test configuration
    instrument_key = "NSE_INDEX|Nifty 50"
    expiry_date = "2024-03-28"  # Update this to a valid expiry date
    bot_id = f"oi_bot_{instrument_key.replace('|', '_')}_{expiry_date}"

    print(f"📋 Test Configuration:")
    print(f"   Instrument: {instrument_key}")
    print(f"   Expiry: {expiry_date}")
    print(f"   Bot ID: {bot_id}")
    print()

    try:
        # Step 1: Activate bot
        print("-" * 80)
        print("STEP 1: Activate Trading Bot")
        print("-" * 80)

        bot_data = await trading_bot_service.activate_bot(
            bot_id=bot_id,
            instrument_key=instrument_key,
            expiry_date=expiry_date,
            lookback_minutes=10,
        )

        print(f"✅ Bot activated successfully!")
        print(f"   Bot ID: {bot_data['bot_id']}")
        print(f"   Active: {bot_data['is_active']}")
        print(f"   Instrument: {bot_data['instrument_key']}")
        print(f"   Expiry: {bot_data['expiry_date']}")
        print(f"   Lookback: {bot_data['lookback_minutes']} minutes")
        print()

        # Step 2: Get bot status
        print("-" * 80)
        print("STEP 2: Get Bot Status")
        print("-" * 80)

        status = await trading_bot_service.get_bot_status(bot_id)
        if status:
            print(f"✅ Bot status retrieved:")
            print(f"   Active: {status.is_active}")
            print(f"   Total Analyses: {status.total_analyses}")
            print(f"   Last Analysis: {status.last_analysis_at or 'Never'}")
        else:
            print("❌ Failed to get bot status")
        print()

        # Step 3: Check for historical data availability
        print("-" * 80)
        print("STEP 3: Check Historical Data")
        print("-" * 80)

        # Check if we have recent snapshots
        snapshots_collection = MongoDB.get_collection("option_chain_snapshots")
        recent_snapshot = await snapshots_collection.find_one(
            {"instrument_key": instrument_key, "expiry_date": expiry_date},
            sort=[("timestamp", -1)],
        )

        if recent_snapshot:
            print(f"✅ Found recent snapshot:")
            print(f"   Timestamp: {recent_snapshot['timestamp']}")
            print(f"   Data available: Yes")
            data_available = True
        else:
            print("⚠️  No option chain snapshots found")
            print(
                "   Please ensure watchlist is configured and snapshots are being collected"
            )
            data_available = False
        print()

        # Step 4: Run analysis (if data available)
        if data_available:
            print("-" * 80)
            print("STEP 4: Run OI Analysis")
            print("-" * 80)

            # Check if we have data from 10 minutes ago
            ten_min_ago = datetime.utcnow() - timedelta(minutes=10)
            ten_min_ago = ten_min_ago.replace(second=0, microsecond=0)
            historical_snapshot = await snapshots_collection.find_one(
                {
                    "instrument_key": instrument_key,
                    "expiry_date": expiry_date,
                    "timestamp": {"$lte": ten_min_ago},
                },
                sort=[("timestamp", -1)],
            )

            if historical_snapshot:
                print("✅ Historical data available (10 minutes ago)")
                print(f"   Historical Timestamp: {historical_snapshot['timestamp']}")
                print()
                print("🔍 Running OI analysis...")

                result = await trading_bot_service.analyze_oi_changes(bot_id)

                if result:
                    print("✅ Analysis completed successfully!")
                    print()
                    print(f"📊 ANALYSIS RESULTS:")
                    print(f"   Timestamp: {result.timestamp}")
                    print(f"   ATM Strike: {result.atm_strike}")
                    print(f"   Spot Price: {result.spot_price}")
                    print(
                        f"   Call OI Change: {result.total_call_oi_change:+,} contracts"
                    )
                    print(
                        f"   Put OI Change: {result.total_put_oi_change:+,} contracts"
                    )
                    print(f"   PCR (OI): {result.pcr_oi}")
                    print(f"   SIGNAL: {result.signal}")
                    print()

                    print(
                        f"📈 Strike-wise Analysis ({len(result.strikes_analyzed)} strikes):"
                    )
                    for strike_data in result.strikes_analyzed:
                        print(f"   Strike {strike_data.strike_price}:")
                        if strike_data.call_oi_change is not None:
                            print(
                                f"      Call OI: {strike_data.call_oi_current:,} "
                                f"({strike_data.call_oi_change:+,}, "
                                f"{strike_data.call_oi_change_percent:+.2f}%)"
                            )
                        if strike_data.put_oi_change is not None:
                            print(
                                f"      Put OI:  {strike_data.put_oi_current:,} "
                                f"({strike_data.put_oi_change:+,}, "
                                f"{strike_data.put_oi_change_percent:+.2f}%)"
                            )
                    print()
                else:
                    print("❌ Analysis failed or returned no results")
                    print(
                        "   Check if ATM strike could be identified or if data is valid"
                    )
            else:
                print("⚠️  No historical data found from 10 minutes ago")
                print("   Analysis requires at least 10 minutes of snapshot history")
                print("   Please wait and try again later")
        else:
            print("-" * 80)
            print("STEP 4: Run OI Analysis - SKIPPED")
            print("-" * 80)
            print("⏭️  Skipping analysis due to missing data")

        print()

        # Step 5: List all active bots
        print("-" * 80)
        print("STEP 5: List Active Bots")
        print("-" * 80)

        active_bots = await trading_bot_service.get_all_active_bots()
        print(f"✅ Found {len(active_bots)} active bot(s):")
        for bot in active_bots:
            print(f"   • {bot['bot_id']}")
            print(f"     Instrument: {bot['instrument_key']}")
            print(f"     Expiry: {bot['expiry_date']}")
        print()

        # Step 6: Deactivate bot
        print("-" * 80)
        print("STEP 6: Deactivate Bot")
        print("-" * 80)

        deactivated = await trading_bot_service.deactivate_bot(bot_id)
        if deactivated:
            print(f"✅ Bot deactivated successfully: {bot_id}")
        else:
            print(f"❌ Failed to deactivate bot: {bot_id}")
        print()

        # Verify deactivation
        final_status = await trading_bot_service.get_bot_status(bot_id)
        if final_status:
            print(f"✅ Verified bot status:")
            print(f"   Active: {final_status.is_active}")
        print()

        print("=" * 80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback

        traceback.print_exc()

    finally:
        # Cleanup
        await MongoDB.close_db()
        print()
        print("👋 Disconnected from MongoDB")


def main():
    """Main entry point"""
    print()
    asyncio.run(test_trading_bot())
    print()


if __name__ == "__main__":
    main()
