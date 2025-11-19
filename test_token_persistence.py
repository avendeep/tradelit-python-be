"""
Test script for Upstox token persistence in MongoDB
"""

import asyncio
from datetime import datetime
from app.db.mongodb import MongoDB
from app.services.upstox_service import upstox_service


async def test_token_persistence():
    """Test saving and loading tokens from database"""

    print("=" * 60)
    print("Testing Upstox Token Persistence")
    print("=" * 60)

    # Connect to database
    print("\n[1] Connecting to MongoDB...")
    try:
        await MongoDB.connect_db()
        print("    Database connected")
    except Exception as e:
        print(f"    Error: {e}")
        return

    # Test 1: Check if token exists in memory
    print("\n[2] Checking current token in memory...")
    if upstox_service.is_token_valid():
        print(f"    Token is valid")
        print(f"    Expires at: {upstox_service._token_expiry}")
    else:
        print("    No valid token in memory")

    # Test 2: Load token from database
    print("\n[3] Loading token from database...")
    loaded = await upstox_service.load_token_from_db()
    if loaded:
        print("    Token loaded successfully")
        print(f"    Access Token: {upstox_service._access_token[:30]}...")
        print(f"    Expires at: {upstox_service._token_expiry}")
    else:
        print("    No valid token found in database")

    # Test 3: Check database collection
    print("\n[4] Checking database collection...")
    try:
        collection = MongoDB.get_collection("upstox_tokens")
        token_doc = await collection.find_one({"_id": "upstox_token"})
        if token_doc:
            print("    Token document found in database:")
            print(f"    - Access Token: {token_doc['access_token'][:30]}...")
            print(f"    - Expires At: {token_doc['expires_at']}")
            print(f"    - Updated At: {token_doc['updated_at']}")
        else:
            print("    No token document found in database")
    except Exception as e:
        print(f"    Error: {e}")

    # Close connection
    print("\n[5] Closing database connection...")
    await MongoDB.close_db()

    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
    print("\nNOTE:")
    print("- Tokens are automatically saved after successful authentication")
    print("- Tokens are loaded on server startup")
    print("- Use /api/v1/upstox/logout to clear tokens from DB")


if __name__ == "__main__":
    asyncio.run(test_token_persistence())
