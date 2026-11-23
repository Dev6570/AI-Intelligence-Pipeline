import os
import logging
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger(__name__)
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv(
    "MONGODB_DATABASE",
    "ai_intelligence_pipeline"
)
_client = None
_database = None
def get_database():
    global _client, _database
    if _database is not None:
        return _database
    if not MONGODB_URI:
        raise ValueError("MONGODB_URI is missing from .env")
    _client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=10000
    )
    _client.admin.command("ping")
    _database = _client[DATABASE_NAME]
    logger.info("MongoDB connected successfully")
    return _database
def create_indexes():
    db = get_database()
    db.startups.create_index(
        "canonicalEntityId",
        unique=True
    )
    db.research_papers.create_index(
        "canonicalEntityId",
        unique=True
    )
    logger.info("Database indexes created")
def close_connection():
    global _client, _database
    if _client is not None:
        _client.close()
    _client = None
    _database = None