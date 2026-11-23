from src.resolver.normalizer import (
    normalize_name,
    create_canonical_id
)
from src.resolver.matcher import (
    compare_names,
    are_duplicates
)
from src.resolver.entity_resolution import (
    resolve_records
)
from src.resolver.validator import (
    validate_resolved_records
)
def test_normalization():
    assert normalize_name("OpenAI Inc.") == "openai"
    assert normalize_name(
        "Microsoft Corporation"
    ) == "microsoft"
    assert normalize_name(
        "Google DeepMind Ltd."
    ) == "google deepmind"
def test_exact_matching():
    assert are_duplicates(
        "OpenAI Inc.",
        "OpenAI"
    )
def test_fuzzy_matching():
    assert compare_names(
        "OpenAI",
        "Open AI"
    ) >= 97
    assert are_duplicates(
        "OpenAI",
        "Open AI"
    )
def test_conflicting_domains():
    assert not are_duplicates(
        "Example AI",
        "Example AI",
        "example.com",
        "different.com"
    )
def test_canonical_id():
    first = create_canonical_id("OpenAI")
    second = create_canonical_id("OpenAI")
    assert first == second
def test_entity_resolution():
    records = [
        {
            "content": {
                "entityName": "OpenAI Inc."
            }
        },
        {
            "content": {
                "entityName": "OpenAI"
            }
        }
    ]
    resolved = resolve_records(
        records,
        "STARTUP"
    )
    assert len(resolved) == 2
    ids = {
        record["entityResolution"]["canonicalEntityId"]
        for record in resolved
    }
    assert len(ids) == 1
def test_validator():
    records = resolve_records(
        [
            {
                "content": {
                    "entityName": "OpenAI"
                }
            }
        ],
        "STARTUP"
    )
    result = validate_resolved_records(records)
    assert result["valid"] is True
if __name__ == "__main__":
    print("Running entity resolution tests...")
    test_normalization()
    test_exact_matching()
    test_fuzzy_matching()
    test_conflicting_domains()
    test_canonical_id()
    test_entity_resolution()
    test_validator()
    print("All tests passed!")