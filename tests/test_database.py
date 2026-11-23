from src.database.db import (
    get_database,
    create_indexes,
    close_connection
)
from src.database.store import (
    store_records,
    get_all_records,
    count_records
)
def test_database_connection():
    db = get_database()
    assert db is not None
    print("MongoDB connection successful!")
def test_database_storage():
    test_collection = "test_entities"
    sample_records = [
        {
            "name": "OpenAI",
            "entityResolution": {
                "canonicalEntityId": "test_openai_001",
                "canonicalName": "OpenAI",
                "aliases": ["Open AI"]
            }
        },
        {
            "name": "Open AI",
            "entityResolution": {
                "canonicalEntityId": "test_openai_001",
                "canonicalName": "OpenAI",
                "aliases": ["Open AI"]
            }
        }
    ]
    store_records(sample_records, test_collection)
    assert count_records(test_collection) == 1
    results = get_all_records(test_collection)
    assert results[0]["canonicalName"] == "OpenAI"
    assert len(results[0]["records"]) == 2
    print("Duplicate grouping test passed!")
if __name__ == "__main__":
    try:
        test_database_connection()
        test_database_storage()
        print("\nAll database tests passed!")
    finally:
        close_connection()