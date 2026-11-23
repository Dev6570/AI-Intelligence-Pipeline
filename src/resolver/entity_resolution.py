import json
import logging
from pathlib import Path
from collections import Counter
from src.resolver.normalizer import (
    normalize_name,
    normalize_domain,
    create_canonical_id
)
from src.resolver.matcher import (
    are_duplicates,
    compare_names
)
logger = logging.getLogger(__name__)
def get_entity_name(record):
    """Extract the entity name from a record."""
    content = record.get("content", {})
    for field in (
        "entityName",
        "companyName",
        "productName",
        "name",
        "title"
    ):
        value = content.get(field)
        if value and str(value).strip():
            return str(value).strip()
    return None
def get_entity_domain(record):
    """Extract an actual entity website domain."""
    content = record.get("content", {})
    website = (
        content.get("website")
        or content.get("website_url")
        or content.get("url")
    )
    return normalize_domain(website)
def choose_canonical_name(cluster):
    """
    Choose the most frequently occurring name.
    Use alphabetical order to break ties.
    """
    names = [
        item["_entity_name"]
        for item in cluster
    ]
    counts = Counter(names)
    return sorted(
        counts,
        key=lambda name: (
            -counts[name],
            len(name),
            name.lower()
        )
    )[0]
def resolve_records(records, entity_type="STARTUP"):
    """
    Group duplicate entities and assign canonical IDs.
    Returns resolved records without deleting original fields.
    """
    prepared = []
    for record in records:
        name = get_entity_name(record)
        if not name:
            logger.warning(
                "Skipping record without entity name"
            )
            continue
        prepared.append({
            **record,
            "_entity_name": name,
            "_normalized_name": normalize_name(name),
            "_domain": get_entity_domain(record)
        })
    prepared.sort(
        key=lambda item: (
            item["_normalized_name"],
            item["_domain"] or ""
        )
    )
    clusters = []
    for record in prepared:
        name = record["_entity_name"]
        domain = record["_domain"]
        matched_cluster = None
        best_score = -1
        for cluster in clusters:
            representative = cluster[0]
            representative_name = (
                representative["_entity_name"]
            )
            representative_domain = (
                representative["_domain"]
            )
            if (
                entity_type.upper() == "STARTUP"
                and domain
                and representative_domain
                and domain == representative_domain
            ):
                matched_cluster = cluster
                best_score = 100
                break
            if are_duplicates(
                name,
                representative_name,
                domain,
                representative_domain
            ):
                score = compare_names(
                    name,
                    representative_name
                )
                if score > best_score:
                    best_score = score
                    matched_cluster = cluster
        if matched_cluster is None:
            clusters.append([record])
        else:
            matched_cluster.append(record)
    resolved = []
    for cluster in clusters:
        canonical_name = choose_canonical_name(cluster)
        domains = sorted({
            item["_domain"]
            for item in cluster
            if item["_domain"]
        })
        canonical_domain = (
            domains[0] if domains else None
        )
        canonical_id = create_canonical_id(
            canonical_name,
            canonical_domain
        )
        aliases = sorted({
            item["_entity_name"]
            for item in cluster
        })
        for item in cluster:
            clean_record = {
                key: value
                for key, value in item.items()
                if not key.startswith("_")
            }
            clean_record["entityResolution"] = {
                "canonicalEntityId": canonical_id,
                "canonicalName": canonical_name,
                "normalizedName": item["_normalized_name"],
                "aliases": aliases,
                "matchMethod": (
                    "EXACT_OR_DOMAIN"
                    if (
                        item["_normalized_name"]
                        == normalize_name(canonical_name)
                        or (
                            entity_type.upper() == "STARTUP"
                            and canonical_domain
                            and item["_domain"] == canonical_domain
                        )
                    )
                    else "FUZZY"
                ),
                "confidence": 1.0 if (
                    item["_normalized_name"]
                    == normalize_name(canonical_name)
                ) else round(
                    compare_names(
                        item["_entity_name"],
                        canonical_name
                    ) / 100,
                    3
                )
            }
            resolved.append(clean_record)
    return resolved
def save_results(records, entity_type, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = (
        output_dir /
        f"{entity_type.lower()}_resolved.json"
    )
    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            records,
            file,
            indent=4,
            ensure_ascii=False
        )
    logger.info(
        "Resolved data saved to %s",
        output_file
    )
    return output_file
def load_json(path):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)
def main():
    project_root = Path(__file__).resolve().parents[2]
    data_dir = project_root / "data"
    output_dir = data_dir / "resolved"
    datasets = [
        ("extracted/startup_extracted.json", "STARTUP"),
        ("research_papers.json", "RESEARCH_PAPER")
    ]
    for filename, entity_type in datasets:
        input_path = data_dir / filename
        if not input_path.exists():
            logger.warning("Dataset not found: %s", input_path)
            continue
        records = load_json(input_path)
        if isinstance(records, dict):
            records = records.get("records", [])
        resolved = resolve_records(records, entity_type)
        save_results(resolved, entity_type, output_dir)
        print(f"\n{entity_type} resolution")
        print("Input records:", len(records))
        print("Resolved records:", len(resolved))
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()