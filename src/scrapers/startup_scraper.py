import asyncio
import aiohttp
import json
import logging
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime, timezone
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
def extract_json_ld(soup):
    """Extract JSON-LD objects from a webpage."""
    results = []
    for script in soup.find_all(
        "script",
        type="application/ld+json"
    ):
        try:
            data = json.loads(script.string or script.get_text())
            if isinstance(data, list):
                results.extend(data)
            else:
                results.append(data)
        except (json.JSONDecodeError, TypeError):
            continue
    return results
def get_entities(data):
    """Handle nested JSON-LD graph objects."""
    for item in data:
        if not isinstance(item, dict):
            continue
        yield item
        graph = item.get("@graph", [])
        if isinstance(graph, list):
            for child in graph:
                if isinstance(child, dict):
                    yield child
def extract_startups(html, source_url):
    soup = BeautifulSoup(html, "lxml")
    records = []
    for item in get_entities(extract_json_ld(soup)):
        entity_type = item.get("@type", [])
        if isinstance(entity_type, str):
            entity_type = [entity_type]
        if "Organization" not in entity_type:
            continue
        name = item.get("name")
        if not name:
            continue
        employee_count = item.get("numberOfEmployees")
        if isinstance(employee_count, dict):
            employee_count = employee_count.get("value")
        try:
            employee_count = (
                int(employee_count)
                if employee_count is not None
                else None
            )
        except (ValueError, TypeError):
            employee_count = None
        records.append({
            "schemaVersion": "1.0",
            "recordType": "STARTUP",
            "source": {
                "name": "Public startup directory",
                "url": source_url
            },
            "content": {
                "entityName": name,
                "data": {
                    "employeeCount": employee_count
                }
            },
            "collectedAt": datetime.now(
                timezone.utc
            ).isoformat()
        })
    return records
async def fetch_page(session, url):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()
    except (
        aiohttp.ClientError,
        asyncio.TimeoutError
    ) as error:
        logger.warning("Failed %s: %s", url, error)
        return None
async def scrape_startups(source_urls):
    results = {}
    connector = aiohttp.TCPConnector(limit=5)
    async with aiohttp.ClientSession(
        connector=connector,
        headers={
            "User-Agent": "AIIntelligencePipeline/1.0"
        }
    ) as session:
        semaphore = asyncio.Semaphore(5)
        async def process(url):
            async with semaphore:
                html = await fetch_page(session, url)
                if not html:
                    return
                for record in extract_startups(html, url):
                    name = record["content"]["entityName"]
                    results.setdefault(name.lower(), record)
        await asyncio.gather(
            *(process(url) for url in source_urls)
        )
    return list(results.values())
def save_startups(records):
    path = OUTPUT_DIR / "startups.json"
    OUTPUT_DIR.mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4, ensure_ascii=False)
    logger.info("Saved %s startup records", len(records))
async def main():
    source_urls = []
    records = await scrape_startups(source_urls)
    save_startups(records)
    print("Startup records:", len(records))
if __name__ == "__main__":
    asyncio.run(main())