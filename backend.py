"""backend.py – OpenAI (>=1.0) backend for Tapix AI assistant
===========================================================

This version uses **openai‑python v1.x** (the current library) instead of the
legacy `openai.ChatCompletion`.  Drop it next to *app.py*, push, and redeploy.

Streamlit Cloud setup
---------------------
Set ``OPENAI_API_KEY`` via the Secrets manager or as an env var.
``OPENAI_MODEL`` – optional, default ``gpt-4o-mini``.

Usage (inside app.py)
---------------------
```python
from backend import generate_ai_response
assistant_reply = generate_ai_response(session_messages)
```
"""
from __future__ import annotations

import os
from typing import List, Dict, Any, Optional

try:
    # openai ≥ 1.0 interface
    from openai import OpenAI, OpenAIError  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "The 'openai' package is not installed. Add 'openai' to your "
        "requirements.txt or run 'pip install openai' locally."
    ) from exc

# ----------------------------------------------------------------------------------
# Configuration helpers
# ----------------------------------------------------------------------------------

def _get_client() -> OpenAI:
    """Return an OpenAI client using env vars or Streamlit secrets."""
    api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing OPENAI_API_KEY. Add it via Streamlit secrets or set the environment variable."
        )
    return OpenAI(api_key=api_key)


DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
SYSTEM_PROMPT = (
    "You are Tapix‑AI, an expert personal finance assistant who can explain "
    "transactions, spot anomalies, and give budgeting tips in simple language."
)

# ----------------------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------------------

def generate_ai_response(
    chat_history: List[Dict[str, str]],
    *,
    extra_context: Optional[Dict[str, Any]] = None,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 512,
    temperature: float = 0.4,
) -> str:
    """Return assistant reply for the given **chat_history**.

    Parameters
    ----------
    chat_history
        List of {"role": "user"|"assistant"|"system", "content": str} dicts.
    extra_context
        Optional dict merged into the system prompt (e.g. Tapix data).
    model, max_tokens, temperature
        Usual OpenAI generation knobs.
    """
    client = _get_client()

    # ----- Build full message list -------------------------------------------------
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": _build_system_prompt(extra_context)},
    ] + chat_history

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,  # type: ignore[arg-type]
            max_tokens=max_tokens,
            temperature=temperature,
        )
    except OpenAIError as e:  # pragma: no cover
        return (
            "⚠️ Sorry, I ran into an error talking to OpenAI: "
            f"{e.__class__.__name__}: {e}.  Please try again later."
        )

    return response.choices[0].message.content.strip()


# ----------------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------------

def _build_system_prompt(extra: Optional[Dict[str, Any]]) -> str:
    """Merge **extra** context into the SYSTEM_PROMPT."""
    if not extra:
        return SYSTEM_PROMPT

    context_lines = ["Here is additional context you can use:"]
    for key, value in extra.items():
        context_lines.append(f"- {key}: {value}")

    return f"{SYSTEM_PROMPT}\n\n" + "\n".join(context_lines)
