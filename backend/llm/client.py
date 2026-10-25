import httpx

from .config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    OLLAMA_TEMPERATURE,
)


def generate_text(system_prompt: str, user_prompt: str) -> str:
    url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/chat"

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "think": False,
        "options": {
            "temperature": OLLAMA_TEMPERATURE,
            "num_predict": 250,
        },
    }

    timeout = httpx.Timeout(
        connect=10.0,
        read=OLLAMA_TIMEOUT,
        write=30.0,
        pool=10.0,
    )

    with httpx.Client(timeout=timeout) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

    text = data.get("message", {}).get("content", "").strip()

    if not text:
        raise RuntimeError("Ollama вернула пустой ответ")

    return text
