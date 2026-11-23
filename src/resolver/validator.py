def validate_resolved_records(records):
    """Validate resolved entity records."""
    errors = []
    seen_ids = set()
    for index, record in enumerate(records):
        resolution = record.get("entityResolution")
        if not isinstance(resolution, dict):
            errors.append(
                f"Record {index}: Missing entityResolution"
            )
            continue
        canonical_id = resolution.get(
            "canonicalEntityId"
        )
        canonical_name = resolution.get(
            "canonicalName"
        )
        if not canonical_id:
            errors.append(
                f"Record {index}: Missing canonical ID"
            )
        if not canonical_name:
            errors.append(
                f"Record {index}: Missing canonical name"
            )
        if canonical_id:
            seen_ids.add(canonical_id)
    return {
        "valid": len(errors) == 0,
        "total_records": len(records),
        "unique_entities": len(seen_ids),
        "duplicate_records": len(records) - len(seen_ids),
        "errors": errors
    }