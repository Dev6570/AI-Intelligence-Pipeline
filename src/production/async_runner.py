import asyncio
import logging
from src.database.pipeline_storage import main as storage_main
logger = logging.getLogger(__name__)
async def run_storage_pipeline():
    logger.info("Starting storage pipeline")
    try:
        await asyncio.to_thread(storage_main)
        logger.info(
            "Storage pipeline completed successfully"
        )
        return {
            "status": "success",
            "message": "Data storage completed"
        }
    except Exception:
        logger.exception(
            "Storage pipeline failed"
        )
        return {
            "status": "failed",
            "message": "Data storage failed"
        }
async def main():
    result = await run_storage_pipeline()
    print(result)
if __name__ == "__main__":
    asyncio.run(main())