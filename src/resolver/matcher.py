from rapidfuzz import fuzz
from src.resolver.normalizer import normalize_name
FUZZY_THRESHOLD = 97
def compare_names(name1, name2):
    first = normalize_name(name1)
    second = normalize_name(name2)
    if not first or not second:
        return 0
    first_compact = first.replace(" ", "")
    second_compact = second.replace(" ", "")
    if first_compact == second_compact:
        return 100
    return fuzz.ratio(first, second)
def are_duplicates(
    name1,
    name2,
    domain1=None,
    domain2=None,
    threshold=FUZZY_THRESHOLD
):
    first = normalize_name(name1)
    second = normalize_name(name2)
    if not first or not second:
        return False
    if domain1 and domain2 and domain1 != domain2:
        return False
    score = compare_names(first, second)
    if score == 100:
        return True
    if domain1 and domain2 and domain1 == domain2:
        return score >= 90
    return score >= threshold