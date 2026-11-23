import json
import logging
from pathlib import Path
from src.database.db import (
    get_database,
    create_indexes,
    close_connection
)
from src.database.store import (
    store_records,
    count_records
)
logger = logging.getLogger(__name__)
def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)
def main():
    project_root = Path(__file__).resolve().parents[2]
    resolved_dir = project_root / "data" / "resolved"
    datasets = [
        ("startup_resolved.json", "startups"),
        ("research_paper_resolved.json", "research_papers")
    ]
    try:
        get_database()
        create_indexes()
        for filename, collection_name in datasets:
            input_path = resolved_dir / filename
            if not input_path.exists():
                logger.warning(
                    "Resolved dataset not found: %s",
                    input_path
                )
                continue
            records = load_json(input_path)
            if isinstance(records, dict):
                records = records.get("records", [])
            stats = store_records(
                records,
                collection_name
            )
            print(f"\n{collection_name}")
            print("Input records:", len(records))
            print("Inserted:", stats["inserted"])
            print("Modified:", stats["modified"])
            print(
                "Total in database:",
                count_records(collection_name)
            )
    finally:
        close_connection()
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()