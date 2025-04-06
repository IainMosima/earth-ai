# app/database/connection.py
import logging
import asyncio
import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mongodb")

load_dotenv()

class MongoDB:
    """MongoDB connection handler class"""
    client: AsyncIOMotorClient = None
    db = None
    is_connected = False

    def __init__(self):
        self.MONGO_URL = os.environ.get("MONGO_URI")
        self.DB_NAME = os.environ.get("DB_NAME")

    def get_db(self):
        """Returns database instance"""
        return self.db

    def get_collection(self, collection_name):
        """Returns a specific collection"""
        return self.db[collection_name]


# Create a singleton instance
db = MongoDB()


async def test_connection():
    """Test MongoDB connection by performing a simple operation"""
    try:
        # The ismaster command is lightweight and doesn't require auth
        await db.client.admin.command('ismaster')
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"MongoDB connection test failed: {e}")
        return False


async def connect_to_mongo():
    """Connect to MongoDB and verify the connection"""
    try:
        # Set a timeout for the connection attempt (in milliseconds)
        db.client = AsyncIOMotorClient(
            db.MONGO_URL,
            serverSelectionTimeoutMS=5000
        )

        # Test connection
        if await test_connection():
            db.db = db.client[db.DB_NAME]
            db.is_connected = True
            logger.info("✅ Successfully connected to MongoDB!")
            logger.info(f"📊 Database: {db.DB_NAME}")

            # Get collection names and counts if any exist
            collections = await db.db.list_collection_names()
            if collections:
                logger.info("📋 Existing collections:")
                for collection in collections:
                    count = await db.db[collection].count_documents({})
                    logger.info(f"   - {collection}: {count} documents")
            else:
                logger.info("📋 No existing collections found")

            return True
        else:
            logger.error("❌ Failed to verify MongoDB connection")
            return False

    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"❌ Could not connect to MongoDB: {e}")
        return False


async def close_mongo_connection():
    """Close MongoDB connection"""
    if db.client:
        db.client.close()
        db.is_connected = False
        logger.info("🔌 MongoDB connection closed")


# If you want to test the connection directly
if __name__ == "__main__":
    async def test():
        connected = await connect_to_mongo()
        if connected:
            print("Connection successful!")
        else:
            print("Connection failed!")
        await close_mongo_connection()


    asyncio.run(test())