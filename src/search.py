import re

from src.database import get_all_incidents


def tokenize(text):
    """Convert text into normalized search terms."""
    return set(re.findall(r"\b[a-zA-Z0-9]+\b", text.lower()))


def search_incidents(query, limit=5, incidents=None):
    """
    Search a supplied dataset or, by default, the saved database incidents.
    """
    query_words = tokenize(query)

    if not query_words:
        return []

    if incidents is None:
        incidents = get_all_incidents()

    matches = []

    searchable_fields = (
        "title",
        "description",
        "category",
        "symptoms",
        "resolution",
        "root_cause",
        "trigger_context",
        "recent_changes",
        "hostname",
        "username",
    )

    for incident in incidents:
        field_text = {
            field: str(incident.get(field) or "").lower()
            for field in searchable_fields
        }

        incident_words = tokenize(" ".join(field_text.values()))
        matched_words = query_words & incident_words

        if not matched_words:
            continue

        score = len(matched_words) / len(query_words)

        for field, weight in (("title", 2), ("symptoms", 1.5)):
            field_words = tokenize(field_text[field])
            score += (
                len(query_words & field_words) / len(query_words)
            ) * weight

        result = incident.copy()
        result["similarity_score"] = round(
            min(score / 4.5, 1.0) * 100,
            1,
        )
        result["matched_terms"] = sorted(matched_words)

        matches.append(result)

    matches.sort(
        key=lambda item: item["similarity_score"],
        reverse=True,
    )

    return matches[:limit]