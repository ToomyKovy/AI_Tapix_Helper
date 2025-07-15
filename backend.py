"""backend.py – OpenAI backend for Tapix AI assistant
=================================================

Provides a single `generate_ai_response()` function that calls the OpenAI
Chat Completion endpoint so your Streamlit app can answer **any** question,
not just the few hard‑coded examples.

Usage
-----

1.  Add `openai` to your **requirements.txt** if it’s not there yet.
2.  Set an environment variable named **OPENAI_API_KEY** (and optionally
    **OPENAI_MODEL**, default is `gpt-4o-mini`).
3.  In `app.py` just do:

    ```python
    from backend import generate_ai_response
    assistant_reply = generate_ai_response(st.session_state["messages"],
                                           extra_context={"transactions": transactions.to_dict("records")})
    ```

That’s it – the function returns the assistant’s reply as a plain string.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

try:
    import openai
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "The 'openai' package is not installed. "
        "Add 'openai' to your requirements.txt or run 'pip install openai' locally."
    ) from exc

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))

SYSTEM_PROMPT = (
    "You are Tapix, a friendly personal‑finance assistant. "
    "You can explain spending patterns, budgeting tips, and transaction details "
    "in clear, helpful language. When data is missing, politely say you don't know."
)


# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------

def generate_ai_response(
    chat_history: List[Dict[str, str]],
    *,
    extra_context: Dict[str, Any] | None = None,
    temperature: float = TEMPERATURE,
) -> str:
    """Return the assistant's reply given the conversation *chat_history*.

    Parameters
    ----------
    chat_history
        A **list** of `{\"role\": ..., \"content\": ...}` messages that already
        includes the user's latest message.
    extra_context
        Optional extra structured data (e.g. Tapix‑cleaned transactions) to pass
        inside a hidden system message.
    temperature
        Sampling temperature for the model (0–2).

    Returns
    -------
    str
        The assistant's reply ready to display in Streamlit.
    """

    if not OPENAI_API_KEY:
        return (
            "⚠️ Your OpenAI key isn't set. Add OPENAI_API_KEY as an environment "
            "variable or Streamlit secret and re‑run the app."
        )

    # ---- Build the message list --------------------------------------------
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    if extra_context is not None:
        messages.append(
            {
                "role": "system",
                "content": "EXTRA_CONTEXT:\n" + str(extra_context),
            }
        )

    # Append the rest of the history (skip any existing system prompts)
    for m in chat_history:
        if m["role"] != "system":
            messages.append(m)

    # ---- Call OpenAI --------------------------------------------------------
    try:
        response = openai.ChatCompletion.create(
            model=DEFAULT_MODEL,
            messages=messages,
            temperature=temperature,
        )
    except Exception as exc:  # pragma: no cover
        return f"🚨 OpenAI API error: {exc}"

    return response.choices[0].message.content.strip()
