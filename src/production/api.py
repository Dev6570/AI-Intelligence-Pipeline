import logging
from fastapi import FastAPI, HTTPException
from src.database.db import get_database
from src.production.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)
app = FastAPI(
    title="AI Intelligence Pipeline API",
    description="API for accessing AI intelligence data",
    version="1.0.0"
)
@app.get("/")
def home():
    return {
        "message": "AI Intelligence Pipeline API",
        "status": "running"
    }
@app.get("/health")
def health_check():
    try:
        db = get_database()
        db.command("ping")
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception:
        logger.exception("Health check failed")
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        )
@app.get("/startups")
def get_startups():
    try:
        db = get_database()
        records = list(
            db.startups.find({}, {"_id": 0}).limit(100)
        )
        return {
            "count": len(records),
            "data": records
        }
    except Exception:
        logger.exception("Startup retrieval failed")
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve startups"
        )
@app.get("/research-papers")
def get_research_papers():
    try:
        db = get_database()
        records = list(
            db.research_papers.find(
                {},
                {"_id": 0}
            ).limit(100)
        )
        return {
            "count": len(records),
            "data": records
        }
    except Exception:
        logger.exception(
            "Research paper retrieval failed"
        )
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve research papers"
        )