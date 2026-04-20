from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


def ask_llm(prompt: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")

    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY environment variable.")

    url = base_url.rstrip("/") + "/chat/completions"

    payload = {
        "model": model,
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a precise repair-policy selector. "
                    "You must return exactly one patch name."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8")
        except Exception:
            body = "<unable to read error body>"
        raise RuntimeError(f"LLM HTTP error {e.code}: {body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"LLM request failed: {e}") from e

    try:
        data = json.loads(raw)
        content = data["choices"][0]["message"]["content"]
    except Exception as e:
        raise RuntimeError(f"Unexpected LLM response format: {raw}") from e

    return content.strip()