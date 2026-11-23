import asyncio
import json
import logging
from pathlib import Path
from src.llm.fallback import extract_text
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = DATA_DIR / "extracted"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
async def process_document(
    input_file,
    record_type,
    source_url
):
    """Read a document and extract structured records."""
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(input_path)
    with open(
        input_path,
        "r",
        encoding="utf-8"
    ) as file:
        raw_text = file.read()
    if not raw_text.strip():
        raise ValueError("Input document is empty")
    records = await extract_text(
        text=raw_text,
        record_type=record_type,
        source_url=source_url
    )
    output = {
        "recordType": record_type,
        "source_url": source_url,
        "total_records": len(records),
        "records": records
    }
    output_file = (
        OUTPUT_DIR /
        f"{record_type.lower()}_extracted.json"
    )
    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False
        )
    logger.info(
        "Extraction completed: %s records",
        len(records)
    )
    logger.info(
        "Output saved: %s",
        output_file
    )
    return output
async def main():
    input_file = DATA_DIR / "sample_article.txt"
    result = await process_document(
        input_file=input_file,
        record_type="STARTUP",
        source_url="https://example.com/company-profile"
    )
    print("\nExtraction Summary")
    print("------------------")
    print("Record type:", result["recordType"])
    print("Records:", result["total_records"])
if __name__ == "__main__":
    asyncio.run(main())