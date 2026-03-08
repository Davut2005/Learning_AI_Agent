"""
Reusable LLM service for interacting with Ollama local REST API.
"""

import requests

OLLAMA_BASE_URL = "http://localhost:11434"
GENERATE_URL = f"{OLLAMA_BASE_URL}/api/generate"
DEFAULT_MODEL = "llama3"


def generate_response(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """
    Send a POST request to the Ollama /api/generate endpoint and return the generated text.
    Uses stream=false for a single JSON response with the full text.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    resp = requests.post(GENERATE_URL, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return data.get("response", "").strip()
