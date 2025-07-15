"""backend.py – OpenAI chat backend for the Tapix Streamlit prototype
=====================================================================
Provides a single `generate_ai_response()` function that can be imported from
`app.py`.  You only need to set the **OPENAI_API_KEY** environment variable (and
optionally **OPENAI_MODEL**) before launching the Streamlit app.

Example on macOS/Linux
----------------------
```
export OPENAI_API_KEY="sk‑..."
streamlit run app.py
```

The helper is intentionally stateless aside from the passed‑in chat history, so
it remains easy to swap in another provider or add advanced features (tool
calling, streaming, etc.) later.
"""
from __future__ import annotations

import os
import sys
import logging
from typing import List, Dict, TypedDict, Sequence

import openai

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
openai.api_key = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "512"))
TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))

SYSTEM_PROMPT = (
    "You are Tapix, a concise and friendly AI financial assistant. "
    "You help users understand their personal finances by analysing their "
    "bank transactions, spotting trends, and offering clear, actionable advice."
)


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------
class ChatMessage(TypedDict):
    role: str
    content: str

# If you prefer a simpler alias:
ChatHistory = Sequence[ChatMessage]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_ai_response(user_message: str, chat_history: ChatHistory | None = None) -> str:
    """Return a model‑generated reply based on the conversation so far.

    Parameters
    ----------
    user_message : str
        The latest human message.
    chat_history : Sequence[ChatMessage] | None
        Prior messages in OpenAI format (each item has "role" + "content").

    Returns
    -------
    str
        The assistant's reply. If an error occurs, a human‑readable message is
        returned instead of raising.
    """
    if not openai.api_key:
        return (
            "⚠️ OPENAI_API_KEY environment variable is missing. "
            "Set it and restart the app to enable AI responses."
        )

    messages: List[ChatMessage] = [{"role": "system", "content": SYSTEM_PROMPT}]
    if chat_history:
        messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})

    try:
        completion = openai.ChatCompletion.create(
            model=DEFAULT_MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            top_p=1,
            stream=False,  # flip to True and yield chunks if you want streaming
        )
        assistant_reply = completion.choices[0].message["content"].strip()
        return assistant_reply or "(No reply)"

    except openai.error.OpenAIError as exc:  # broad but keeps imports minimal
        logger.exception("OpenAI API error: %s", exc)
        return f"⚠️ Sorry, I couldn’t reach the AI service: {exc}"

    except Exception:  # noqa: BLE001 – catch‑all so the Streamlit app keeps running
        logger.exception("Unexpected error while contacting the model")
        return "⚠️ An unexpected error occurred while generating the response."


# ---------------------------------------------------------------------------
# CLI helper for quick manual tests ------------------------------------------------
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Tapix backend quick‑chat. Type 'exit' to quit.")
    history: List[ChatMessage] = []
    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            sys.exit(0)

        if user_input.lower() in {"exit", "quit"}:
            print("Bye!")
            break

        reply = generate_ai_response(user_input, history)
        print(f"AI: {reply}\n")
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": reply})
