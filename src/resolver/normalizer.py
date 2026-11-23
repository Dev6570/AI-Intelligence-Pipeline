import re
import unicodedata
LEGAL_SUFFIXES = {
    "inc",
    "incorporated",
    "llc",
    "ltd",
    "limited",
    "corp",
    "corporation",
    "co"
}
def normalize_name(name):
    """
    Normalize an entity name for comparison.
    Examples:
    OpenAI Inc. -> openai
    Open AI    -> open ai
    """
    if not name:
        return ""
    name = unicodedata.normalize("NFKC", str(name))
    name = name.lower().strip()
    name = name.replace("&", " and ")
    name = re.sub(r"[^\w\s]", " ", name)
    words = name.split()
    while words and words[-1] in LEGAL_SUFFIXES:
        words.pop()
    return " ".join(words)
def normalize_domain(url):
    """
    Extract a normalized domain from a URL.
    """
    if not url:
        return None
    from urllib.parse import urlparse
    value = str(url).strip()
    if "://" not in value:
        value = "https://" + value
    try:
        domain = urlparse(value).hostname
        if not domain:
            return None
        domain = domain.lower().removeprefix("www.")
        return domain
    except ValueError:
        return None
def create_canonical_id(name, domain=None):
    """
    Generate a deterministic entity identifier.
    """
    import hashlib
    identity = (
        f"domain:{domain}"
        if domain
        else f"name:{normalize_name(name)}"
    )
    digest = hashlib.sha256(
        identity.encode("utf-8")
    ).hexdigest()[:16]
    return f"ENT_{digest.upper()}"