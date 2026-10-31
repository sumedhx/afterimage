import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"


def explain_similar_incidents(current_issue, historical_incidents):
    """Use the local AI model to explain relevant historical incidents."""

    if not historical_incidents:
        return "No matching historical incidents were found to analyze."

    history = []

    for incident in historical_incidents[:3]:
        history.append(
            f"""
Incident ID: {incident.get('id')}
Title: {incident.get('title')}
Category: {incident.get('category')}
Symptoms: {incident.get('symptoms')}
Description: {incident.get('description')}
Root cause: {incident.get('root_cause')}
Resolution: {incident.get('resolution')}
Similarity score: {incident.get('similarity_score')}%
"""
        )

    historical_context = "\n".join(history)

    prompt = f"""
You are Afterimage, a local AI assistant for IT support engineers.

Analyze the current IT issue using only the historical incidents provided.

CURRENT ISSUE:
{current_issue}

HISTORICAL INCIDENTS:
{historical_context}

Provide your response in these sections:
1. Similarities: Explain which symptoms overlap with previous incidents.
2. Historical findings: Summarize relevant causes and resolutions from the records.
3. Suggested checks: Recommend safe diagnostic checks based on the evidence.
4. Uncertainty: Explain what cannot be concluded from the available information.

Rules:
- Do not invent historical facts.
- Clearly distinguish recorded facts from suggestions.
- Do not claim that a historical root cause is definitely the current cause.
- Do not recommend destructive actions or execute commands.
- If the records are insufficient, say so.
- Keep the response concise and practical.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
        )
        response.raise_for_status()

        result = response.json()
        return result.get("response", "").strip() or (
            "The AI returned an empty response."
        )

    except requests.exceptions.ConnectionError:
        return (
            "Could not connect to Ollama. Make sure Ollama is running "
            "and the qwen2.5:1.5b model is installed."
        )

    except requests.exceptions.Timeout:
        return "The AI request timed out. Please try again."

    except requests.exceptions.RequestException as error:
        return f"AI request failed: {error}"

    except ValueError:
        return "Ollama returned an invalid response."