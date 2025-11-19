"""
Test script for Upstox Option Chain API integration
"""

import asyncio
from datetime import datetime, timedelta
from app.db.mongodb import MongoDB
from app.services.upstox_service import upstox_service


async def test_option_chain():
    """Test the option chain API integration"""

    print("=" * 70)
    print("Testing Upstox Option Chain API Integration")
    print("=" * 70)

    # Connect to database and load token
    print("\n[1] Connecting to MongoDB and loading token...")
    try:
        await MongoDB.connect_db()
        await upstox_service.load_token_from_db()

        if not upstox_service.is_token_valid():
            print("    ✗ No valid token found. Please authenticate first.")
            print("    Run: uvicorn main:app --reload")
            print("    Then: GET /api/v1/upstox/login")
            await MongoDB.close_db()
            return

        print("    ✓ Authenticated successfully")
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return

    # Test 1: Fetch Nifty 50 option chain
    print("\n[2] Fetching Nifty 50 option chain...")

    # Calculate next Thursday (typical Nifty expiry)
    today = datetime.now()
    days_ahead = 3 - today.weekday()  # Thursday = 3
    if days_ahead <= 0:
        days_ahead += 7
    next_thursday = today + timedelta(days=days_ahead)
    expiry_date = next_thursday.strftime("%Y-%m-%d")

    print(f"    Instrument: NSE_INDEX|Nifty 50")
    print(f"    Expiry Date: {expiry_date}")

    try:
        option_chain = await upstox_service.get_option_chain(
            instrument_key="NSE_INDEX|Nifty 50", expiry_date=expiry_date
        )

        if option_chain:
            print("    ✓ Option chain fetched successfully")

            # Display summary
            data = option_chain.get("data", [])
            print(f"\n    Summary:")
            print(f"    - Total strikes: {len(data)}")

            if data:
                print(f"\n    Sample data (first strike):")
                first_strike = data[0]
                print(f"    - Strike Price: {first_strike.get('strike_price')}")
                print(f"    - Expiry: {first_strike.get('expiry')}")
                print(
                    f"    - Underlying Spot: {first_strike.get('underlying_spot_price')}"
                )

                # Call option info
                call_option = first_strike.get("call_options", {})
                if call_option:
                    call_market = call_option.get("market_data", {})
                    print(f"\n    Call Option:")
                    print(f"    - LTP: {call_market.get('ltp')}")
                    print(f"    - Volume: {call_market.get('volume')}")
                    print(f"    - OI: {call_market.get('oi')}")

                # Put option info
                put_option = first_strike.get("put_options", {})
                if put_option:
                    put_market = put_option.get("market_data", {})
                    print(f"\n    Put Option:")
                    print(f"    - LTP: {put_market.get('ltp')}")
                    print(f"    - Volume: {put_market.get('volume')}")
                    print(f"    - OI: {put_market.get('oi')}")
        else:
            print("    ✗ No data returned")

    except Exception as e:
        print(f"    ✗ Error: {e}")

    # Test 2: Fetch Bank Nifty option chain
    print("\n[3] Fetching Bank Nifty option chain...")
    print(f"    Instrument: NSE_INDEX|Bank Nifty")
    print(f"    Expiry Date: {expiry_date}")

    try:
        option_chain = await upstox_service.get_option_chain(
            instrument_key="NSE_INDEX|Bank Nifty", expiry_date=expiry_date
        )

        if option_chain:
            print("    ✓ Bank Nifty option chain fetched successfully")
            data = option_chain.get("data", [])
            print(f"    - Total strikes: {len(data)}")
        else:
            print("    ✗ No data returned")

    except Exception as e:
        print(f"    ✗ Error: {e}")

    # Close database
    print("\n[4] Closing database connection...")
    await MongoDB.close_db()

    print("\n" + "=" * 70)
    print("Test Complete")
    print("=" * 70)
    print("\nAPI Endpoints Available:")
    print(
        "  GET  /api/v1/option-chain?instrument_key=NSE_INDEX|Nifty 50&expiry_date=YYYY-MM-DD"
    )
    print("  POST /api/v1/option-chain")
    print("  GET  /api/v1/option-chain/instruments")
    print("\nDocumentation:")
    print("  http://localhost:8000/docs")


if __name__ == "__main__":
    asyncio.run(test_option_chain())
