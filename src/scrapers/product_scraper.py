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
def extract_products(html, source_url):
    soup = BeautifulSoup(html, "lxml")
    records = []
    for script in soup.find_all(
        "script",
        type="application/ld+json"
    ):
        try:
            data = json.loads(
                script.string or script.get_text()
            )
        except (json.JSONDecodeError, TypeError):
            continue
        objects = data if isinstance(data, list) else [data]
        for item in objects:
            if not isinstance(item, dict):
                continue
            candidates = [item]
            if isinstance(item.get("@graph"), list):
                candidates.extend(item["@graph"])
            for product in candidates:
                if not isinstance(product, dict):
                    continue
                entity_type = product.get("@type", [])
                if isinstance(entity_type, str):
                    entity_type = [entity_type]
                if not any(
                    kind in entity_type
                    for kind in [
                        "SoftwareApplication",
                        "Product"
                    ]
                ):
                    continue
                name = product.get("name")
                if not name:
                    continue
                offers = product.get("offers", {})
                if isinstance(offers, list):
                    offers = offers[0] if offers else {}
                if not isinstance(offers, dict):
                    offers = {}
                price = offers.get("price")
                if price is None:
                    pricing_model = "UNKNOWN"
                elif str(price) == "0":
                    pricing_model = "FREE"
                else:
                    pricing_model = "PAID"
                records.append({
                    "schemaVersion": "1.0",
                    "recordType": "PRODUCT",
                    "source": {
                        "name": "Public AI product directory",
                        "url": source_url
                    },
                    "content": {
                        "entityName": name,
                        "startupName": None,
                        "pricingModel": pricing_model,
                        "description": product.get(
                            "description"
                        )
                    },
                    "collectedAt": datetime.now(
                        timezone.utc
                    ).isoformat()
                })
    return records
async def scrape_products(source_urls):
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
                try:
                    async with session.get(url) as response:
                        response.raise_for_status()
                        html = await response.text()
                    records = extract_products(html, url)
                    for record in records:
                        name = record["content"]["entityName"]
                        results.setdefault(
                            name.lower(),
                            record
                        )
                except (
                    aiohttp.ClientError,
                    asyncio.TimeoutError
                ) as error:
                    logger.warning(
                        "Failed %s: %s",
                        url,
                        error
                    )
        await asyncio.gather(
            *(process(url) for url in source_urls)
        )
    return list(results.values())
async def main():
    source_urls = []
    records = await scrape_products(source_urls)
    OUTPUT_DIR.mkdir(exist_ok=True)
    with open(
        OUTPUT_DIR / "products.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            records,
            file,
            indent=4,
            ensure_ascii=False
        )
    print("Product records:", len(records))
if __name__ == "__main__":
    asyncio.run(main())