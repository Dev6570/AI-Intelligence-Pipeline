import logging
from pymongo import ReplaceOne
from src.database.db import get_database
logger = logging.getLogger(__name__)
def store_records(records, collection_name):
    db = get_database()
    collection = db[collection_name]
    grouped = {}
    for record in records:
        resolution = record.get("entityResolution", {})
        canonical_id = resolution.get("canonicalEntityId")
        if not canonical_id:
            logger.warning("Skipping record without canonical ID")
            continue
        if canonical_id not in grouped:
            grouped[canonical_id] = {
                "canonicalEntityId": canonical_id,
                "canonicalName": resolution.get("canonicalName"),
                "aliases": resolution.get("aliases", []),
                "records": []
            }
        grouped[canonical_id]["records"].append(record)
    operations = []
    for canonical_id, document in grouped.items():
        operations.append(
            ReplaceOne(
                {"canonicalEntityId": canonical_id},
                document,
                upsert=True
            )
        )
    if not operations:
        return {"inserted": 0, "modified": 0}
    result = collection.bulk_write(
        operations,
        ordered=False
    )
    stats = {
        "inserted": result.upserted_count,
        "modified": result.modified_count
    }
    logger.info("%s storage: %s", collection_name, stats)
    return stats
def get_all_records(collection_name):
    db = get_database()
    return list(db[collection_name].find({}, {"_id": 0}))
def count_records(collection_name):
    db = get_database()
    return db[collection_name].count_documents({})