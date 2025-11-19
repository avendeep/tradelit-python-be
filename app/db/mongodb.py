from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
from typing import Optional


class MongoDB:
    """MongoDB database connection manager"""

    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect_db(cls):
        """Create database connection"""
        try:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
            cls.database = cls.client[settings.DATABASE_NAME]
            # Verify connection
            await cls.client.server_info()
            print(f"✅ Connected to MongoDB: {settings.DATABASE_NAME}")
        except Exception as e:
            print(f"❌ Could not connect to MongoDB: {e}")
            raise e

    @classmethod
    async def close_db(cls):
        """Close database connection"""
        if cls.client:
            cls.client.close()
            print("🔌 MongoDB connection closed")

    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Get database instance"""
        if cls.database is None:
            raise Exception("Database not initialized. Call connect_db() first.")
        return cls.database

    @classmethod
    def get_collection(cls, collection_name: str):
        """Get a specific collection"""
        db = cls.get_database()
        return db[collection_name]


# Helper function to get database instance
async def get_database() -> AsyncIOMotorDatabase:
    """Dependency to get database instance"""
    return MongoDB.get_database()
