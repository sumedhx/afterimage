import re
from functools import lru_cache

import requests


OLLAMA_URL = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text:latest"
EMBED_TIMEOUT = 60

SEARCHABLE_FIELDS = (
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

FIELD_WEIGHTS = {
    "title": 3.0,
    "symptoms": 2.5,
    "description": 2.0,
    "root_cause": 1.5,
    "resolution": 1.2,
    "category": 1.0,
    "trigger_context": 1.0,
    "recent_changes": 1.0,
    "hostname": 0.5,
    "username": 0.5,
}

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were",
    "be", "been", "being", "to", "of", "in", "on",
    "at", "for", "from", "with", "by", "and", "or",
    "but", "while", "when", "where", "after", "before",
    "it", "its", "this", "that", "these", "those",
    "my", "our", "their", "his", "her", "i", "we",
    "user", "system", "issue", "problem", "error",
    "please", "keeps", "keep", "still", "very",
}

ALIASES = {
    "saving": "save",
    "saved": "save",
    "saves": "save",
    "freezes": "freeze",
    "freezing": "freeze",
    "frozen": "freeze",
    "filtering": "filter",
    "filtered": "filter",
    "filters": "filter",
    "disconnecting": "disconnect",
    "disconnected": "disconnect",
    "disconnects": "disconnect",
    "reconnecting": "reconnect",
    "reconnected": "reconnect",
    "reconnects": "reconnect",
    "printing": "print",
    "printed": "print",
    "prints": "print",
    "hanging": "hang",
    "hangs": "hang",
    "crashing": "crash",
    "crashed": "crash",
    "crashes": "crash",
    "failing": "fail",
    "failed": "fail",
    "fails": "fail",
    "failure": "fail",
    "slowly": "slow",
    "slower": "slow",
    "can't": "cannot",
    "unable": "cannot",
    "logon": "login",
    "sign-in": "login",
    "signin": "login",
}

# Actions describing what the user was trying to do.
# These are more discriminative than general symptoms such as freeze.
TASK_ACTIONS = {
    "save", "filter", "print", "open", "install", "update",
    "connect", "disconnect", "reconnect", "login", "sign",
    "sync", "delete", "download", "upload", "access", "ping",
    "restart", "boot", "scan", "launch", "start", "stop",
    "load", "authenticate",
}

TECHNICAL_TERMS = {
    "excel", "outlook", "windows", "printer", "queue",
    "access", "point", "wifi", "network", "vpn", "dns",
    "dhcp", "profile", "onedrive", "office", "laptop",
    "desktop", "monitor", "application", "database",
    "server", "switch",
}


def _as_text(value):
    """Convert a field value into searchable text."""
    if value is None:
        return ""

    if isinstance(value, (list, tuple, set)):
        return " ".join(
            str(item) for item in value if item is not None
        )

    return str(value)


def tokenize(text):
    """Normalize words and common technical phrases."""
    text = _as_text(text).lower()

    # Normalize phrases before splitting into individual words.
    text = re.sub(r"\blog\s+in\b", " login ", text)
    text = re.sub(r"\blog\s+on\b", " login ", text)
    text = re.sub(r"\bsign\s+in\b", " login ", text)
    text = re.sub(r"\bsign\s+on\b", " login ", text)

    raw_tokens = re.findall(r"[a-z0-9]+", text)

    normalized = []

    for token in raw_tokens:
        token = ALIASES.get(token, token)

        if token in STOPWORDS or len(token) < 2:
            continue

        # Basic fallback normalization for common inflections.
        if token not in ALIASES.values():
            if len(token) > 5 and token.endswith("ies"):
                token = token[:-3] + "y"
            elif len(token) > 5 and token.endswith("ing"):
                token = token[:-3]

                if len(token) > 2 and token[-1] == token[-2]:
                    token = token[:-1]
            elif len(token) > 4 and token.endswith("ed"):
                token = token[:-2]
            elif len(token) > 4 and token.endswith("s"):
                token = token[:-1]

        token = ALIASES.get(token, token)

        if token not in STOPWORDS and len(token) > 1:
            normalized.append(token)

    return normalized


def _field_tokens(incident):
    return {
        field: set(tokenize(incident.get(field)))
        for field in SEARCHABLE_FIELDS
    }


def _incident_text(incident):
    """Build text for semantic embedding."""
    parts = []

    for field in SEARCHABLE_FIELDS:
        value = _as_text(incident.get(field)).strip()

        if value:
            parts.append(f"{field.replace('_', ' ')}: {value}")

    return "\n".join(parts)


@lru_cache(maxsize=2048)
def _cached_embedding(text):
    """Get an embedding from the local Ollama service."""
    if not text.strip():
        return None

    response = requests.post(
        f"{OLLAMA_URL}/api/embed",
        json={
            "model": EMBED_MODEL,
            "input": text,
        },
        timeout=EMBED_TIMEOUT,
    )

    response.raise_for_status()

    embeddings = response.json().get("embeddings", [])

    return embeddings[0] if embeddings else None


def _embed(text):
    """Return an embedding or fall back if Ollama is unavailable."""
    try:
        return _cached_embedding(text)
    except (requests.RequestException, ValueError, KeyError, TypeError):
        return None


def _cosine_similarity(vector_a, vector_b):
    if not vector_a or not vector_b:
        return 0.0

    if len(vector_a) != len(vector_b):
        return 0.0

    dot = sum(a * b for a, b in zip(vector_a, vector_b))
    norm_a = sum(a * a for a in vector_a) ** 0.5
    norm_b = sum(b * b for b in vector_b) ** 0.5

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def _term_weight(term):
    weight = 1.0

    if term in TECHNICAL_TERMS:
        weight += 0.5

    if term in TASK_ACTIONS:
        weight += 1.0

    return weight


def _keyword_score(query_tokens, incident):
    """Calculate weighted keyword coverage across incident fields."""
    query_terms = set(query_tokens)

    if not query_terms:
        return 0.0, []

    fields = _field_tokens(incident)

    boosts = {
        "title": 1.0,
        "symptoms": 0.90,
        "description": 0.75,
        "root_cause": 0.65,
        "resolution": 0.55,
        "category": 0.60,
        "trigger_context": 0.55,
        "recent_changes": 0.55,
        "hostname": 0.35,
        "username": 0.35,
    }

    total_weight = 0.0
    matched_weight = 0.0
    matched_terms = []

    for term in query_terms:
        weight = _term_weight(term)
        total_weight += weight

        # A term earns credit based on its strongest field match.
        best_boost = max(
            (
                boosts[field]
                for field, terms in fields.items()
                if term in terms
            ),
            default=0.0,
        )

        if best_boost:
            matched_weight += weight * best_boost
            matched_terms.append(term)

    score = matched_weight / total_weight if total_weight else 0.0

    return score, sorted(matched_terms)


def _action_mismatch(query_tokens, incident):
    """
    Detect when an incident describes a different task.

    Example: a query about saving should not rank a filtering
    incident highly merely because both mention Excel and freezing.
    """
    query_actions = set(query_tokens) & TASK_ACTIONS

    if not query_actions:
        return False

    title_tokens = set(tokenize(incident.get("title")))
    symptom_tokens = set(tokenize(incident.get("symptoms")))
    description_tokens = set(tokenize(incident.get("description")))

    # Actions explicitly mentioned in the incident's main description.
    incident_actions = (
        title_tokens | symptom_tokens | description_tokens
    ) & TASK_ACTIONS

    # If the incident describes a different explicit action,
    # treat it as an action mismatch.
    if incident_actions and not (query_actions & incident_actions):
        return True

    return False


def _is_relevant(keyword_score, semantic_score, title_score):
    """Avoid returning incidents supported only by broad similarity."""
    if semantic_score is None:
        return keyword_score >= 0.20

    return (
        keyword_score >= 0.25
        or title_score >= 0.72
        or (
            semantic_score >= 0.68
            and keyword_score >= 0.12
        )
    )


def search_incidents(query, limit=5, incidents=None):
    """
    Hybrid incident search using semantic similarity and keywords.

    Semantic search uses local Ollama. Keyword search remains available
    if Ollama cannot provide embeddings.
    """
    query = _as_text(query).strip()

    if not query:
        return []

    if incidents is None:
        from src.database import get_all_incidents
        incidents = get_all_incidents()

    if not incidents:
        return []

    query_tokens = tokenize(query)

    if not query_tokens:
        return []

    query_embedding = _embed(query)
    results = []

    for incident in incidents:
        keyword_score, matched_terms = _keyword_score(
            query_tokens,
            incident,
        )

        title = _as_text(incident.get("title"))
        full_text = _incident_text(incident)

        semantic_score = None
        title_score = 0.0

        if query_embedding is not None:
            full_embedding = _embed(full_text)
            title_embedding = _embed(title)

            if full_embedding is not None:
                semantic_score = max(
                    0.0,
                    _cosine_similarity(
                        query_embedding,
                        full_embedding,
                    ),
                )

            if title_embedding is not None:
                title_score = max(
                    0.0,
                    _cosine_similarity(
                        query_embedding,
                        title_embedding,
                    ),
                )

        action_mismatch = _action_mismatch(
            query_tokens,
            incident,
        )

        # Reject clear action conflicts rather than merely lowering
        # their score. This helps separate saving from filtering, etc.
        if action_mismatch:
            continue

        if not _is_relevant(
            keyword_score,
            semantic_score,
            title_score,
        ):
            continue

        if semantic_score is None:
            combined_score = keyword_score
        else:
            combined_score = (
                0.45 * keyword_score
                + 0.30 * title_score
                + 0.25 * semantic_score
            )

        combined_score = max(0.0, min(1.0, combined_score))

        result = dict(incident)
        result["similarity_score"] = round(combined_score * 100, 1)
        result["semantic_score"] = (
            round(semantic_score * 100, 1)
            if semantic_score is not None
            else None
        )
        result["title_score"] = round(title_score * 100, 1)
        result["keyword_score"] = round(keyword_score * 100, 1)
        result["matched_terms"] = matched_terms

        results.append(result)


    # Remove low-confidence matches before displaying results.
    MIN_SIMILARITY_SCORE = 60.0
    
    results = [
        item for item in results
        if item["similarity_score"] >= MIN_SIMILARITY_SCORE
    ]

    results.sort(
        key=lambda item: (
            item["similarity_score"],
            item["keyword_score"],
            item["title_score"],
        ),
        reverse=True,
    )

    return results[:limit]