
import json
import re
import urllib.request
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]

EXISTING_FILE = (
    PROJECT_ROOT / "data" / "extracted" / "product_extracted.json"
)

ADDITIONAL_FILE = (
    PROJECT_ROOT / "data" / "extracted" / "product_additional.json"
)

MERGED_FILE = (
    PROJECT_ROOT / "data" / "extracted" / "product_extracted_merged.json"
)

# TiorAI public dataset
DATASET_URL = (
    "https://raw.githubusercontent.com/"
    "tioraicom/ai-tools-dataset/main/data/ai-tools.json"
)


def normalize_name(name):
    """Normalize product names for duplicate detection."""
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def normalize_url(url):
    """Normalize URLs to compare product websites."""
    if not url:
        return ""

    try:
        parsed = urlparse(url.strip())
        host = (parsed.hostname or "").lower()

        if host.startswith("www."):
            host = host[4:]

        return host
    except Exception:
        return ""


def get_product_name(record):
    """Read product name from the existing dataset format."""
    return (
        record.get("content", {}).get("entityName")
        or record.get("name")
        or record.get("title")
        or ""
    )


def get_existing_url(record):
    """Read the existing product website."""
    return (
        record.get("content", {}).get("website")
        or record.get("source", {}).get("url")
        or ""
    )


def map_pricing(pricing_models):
    """Map source pricing labels to the project enum."""
    models = {
        str(value).strip().lower()
        for value in (pricing_models or [])
    }

    if "freemium" in models:
        return "FREEMIUM"

    if "paid" in models:
        return "PAID"

    if "free" in models or "open source" in models:
        return "FREE"

    # Do not guess when the source only says Free Trial.
    return None


def download_dataset():
    """Download the public TiorAI JSON dataset."""
    print("Downloading additional product dataset...")

    request = urllib.request.Request(
        DATASET_URL,
        headers={"User-Agent": "AI-Intelligence-Pipeline/1.0"}
    )

    with urllib.request.urlopen(request, timeout=40) as response:
        data = json.loads(response.read().decode("utf-8"))

    if not isinstance(data, list):
        raise ValueError("Unexpected dataset format. Expected a JSON list.")

    print("Downloaded records:", len(data))
    return data


def load_existing_products():
    """Load existing products without modifying the original file."""
    if not EXISTING_FILE.exists():
        raise FileNotFoundError(
            f"Existing product file not found: {EXISTING_FILE}"
        )

    with open(EXISTING_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Existing product file must contain a JSON list.")

    return data


def build_existing_indexes(products):
    """Build duplicate-detection indexes."""
    names = set()
    websites = set()

    for product in products:
        name = get_product_name(product)
        website = get_existing_url(product)

        if name:
            names.add(normalize_name(name))

        if website:
            websites.add(normalize_url(website))

    return names, websites


def convert_product(product):
    """Convert TiorAI data into the project's product structure."""
    name = product.get("name")
    website = product.get("official_url")

    if not name or not website:
        return None

    parsed = urlparse(website)

    # Require a valid HTTPS official product URL.
    if parsed.scheme != "https" or not parsed.hostname:
        return None

    pricing_model = map_pricing(product.get("pricing_model"))

    return {
        "schemaVersion": "1.0",
        "recordType": "PRODUCT",
        "source": {
            "name": "TiorAI AI Tools Dataset (CC BY 4.0)",
            "url": website,
            "datasetUrl": DATASET_URL
        },
        "content": {
            "entityName": name.strip(),
            "startupName": None,
            "pricingModel": pricing_model,
            "description": product.get("short_description"),
            "website": website,
            "category": product.get("primary_category"),
            "secondaryCategory": product.get("secondary_category"),
            "platform": product.get("platform", []),
            "openSource": product.get("open_source"),
            "apiAvailable": product.get("api_available"),
            "lastVerified": product.get("last_verified")
        },
        "collectedAt": datetime.now(timezone.utc).isoformat()
    }


def scrape_additional_products():
    """Collect only products not already present in the existing dataset."""
    existing = load_existing_products()
    source_records = download_dataset()

    existing_names, existing_websites = build_existing_indexes(existing)

    additional = []
    skipped_duplicates = 0
    skipped_invalid = 0

    for product in source_records:
        converted = convert_product(product)

        if not converted:
            skipped_invalid += 1
            continue

        name = converted["content"]["entityName"]
        website = converted["content"]["website"]

        normalized_name = normalize_name(name)
        normalized_website = normalize_url(website)

        if (
            normalized_name in existing_names
            or normalized_website in existing_websites
        ):
            skipped_duplicates += 1
            continue

        additional.append(converted)

        # Also prevent duplicates within the downloaded dataset.
        existing_names.add(normalized_name)
        existing_websites.add(normalized_website)

    # Save only additional records.
    ADDITIONAL_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(ADDITIONAL_FILE, "w", encoding="utf-8") as file:
        json.dump(additional, file, indent=4, ensure_ascii=False)

    # Create a separate merged file; preserve the original.
    merged = existing + additional

    with open(MERGED_FILE, "w", encoding="utf-8") as file:
        json.dump(merged, file, indent=4, ensure_ascii=False)

    print("\n========== PRODUCT SCRAPING SUMMARY ==========")
    print("Existing products:", len(existing))
    print("Downloaded source records:", len(source_records))
    print("Additional unique products:", len(additional))
    print("Skipped duplicates:", skipped_duplicates)
    print("Skipped invalid records:", skipped_invalid)
    print("Final merged product count:", len(merged))
    print("\nAdditional file:", ADDITIONAL_FILE)
    print("Merged file:", MERGED_FILE)


if __name__ == "__main__":
    scrape_additional_products()
