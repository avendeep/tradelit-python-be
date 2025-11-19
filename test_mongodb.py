"""Test MongoDB connection"""

from motor.motor_asyncio import AsyncIOMotorClient
import asyncio


async def test_mongodb():
    try:
        print("🔍 Testing MongoDB connection...")
        client = AsyncIOMotorClient(
            "mongodb://localhost:27017", serverSelectionTimeoutMS=5000
        )

        # Test connection
        await client.server_info()
        print("✅ MongoDB connection successful!")

        # Access database
        db = client["trade_lit_db"]
        print(f"✅ Database 'trade_lit_db' is accessible")

        # List collections
        collections = await db.list_collection_names()
        if collections:
            print(f"📦 Existing collections: {', '.join(collections)}")
        else:
            print("📦 No collections yet (new database)")

        # Test insert
        test_collection = db["test_connection"]
        result = await test_collection.insert_one(
            {"test": "connection", "status": "success"}
        )
        print(f"✅ Test document inserted with ID: {result.inserted_id}")

        # Clean up test document
        await test_collection.delete_one({"_id": result.inserted_id})
        print("🧹 Test document cleaned up")

        client.close()
        print("\n🎉 MongoDB is ready for TradeLit!")
        return True

    except Exception as e:
        print(f"\n❌ MongoDB connection failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure MongoDB is installed")
        print("   2. Start MongoDB service:")
        print("      - Windows: net start MongoDB")
        print("      - Or run: mongod")
        print("   3. Download MongoDB: https://www.mongodb.com/try/download/community")
        return False


if __name__ == "__main__":
    asyncio.run(test_mongodb())
