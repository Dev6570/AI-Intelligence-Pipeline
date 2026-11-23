from typing import Optional, Literal
from pydantic import BaseModel, Field
class StartupRecord(BaseModel):
    schemaVersion: str = "1.0"
    recordType: Literal["STARTUP"] = "STARTUP"
    source: dict
    content: dict = Field(
        description="Must contain entityName and data"
    )
    collectedAt: str
class ProductRecord(BaseModel):
    schemaVersion: str = "1.0"
    recordType: Literal["PRODUCT"] = "PRODUCT"
    source: dict
    content: dict = Field(
        description=(
            "Must contain startupName and pricingModel"
        )
    )
    collectedAt: str
class ResearchPaperRecord(BaseModel):
    schemaVersion: str = "1.0"
    recordType: Literal["RESEARCH_PAPER"] = "RESEARCH_PAPER"
    content: dict = Field(
        description=(
            "Must contain title, authors, paper_url, "
            "github_url, github_stars and published_date"
        )
    )
class ExtractedData(BaseModel):
    recordType: Literal[
        "STARTUP",
        "PRODUCT",
        "RESEARCH_PAPER"
    ]
    records: list[dict] = Field(default_factory=list)