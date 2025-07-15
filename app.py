"""app.py – Tapix AI Finance Assistant (Streamlit)
================================================
Revamped, on‑brand Streamlit front‑end inspired by the Tapix “with enrichment” mock‑up.
Adds a fresh green gradient background, glassy cards, rounded buttons, and a cleaner
chat experience while keeping the original logic intact.
"""
from __future__ import annotations

import os
from datetime import datetime
from typing import List, Dict, Any, Optional

import pandas as pd
import streamlit as st

# ----------------------------------------------------------------------------
# Backend – replace generate_ai_response with your actual implementation.
# ----------------------------------------------------------------------------
try:
    from backend import generate_ai_response  # type: ignore  # pragma: no‑cover
except ModuleNotFoundError:
    # lightweight fallback so the app still launches without backend.py
    def generate_ai_response(messages: List[Dict[str, str]], extra_context: Dict[str, Any] | None = None) -> str:  # type: ignore[override]
        return (
            "🚧 *Backend not wired yet – this is a stubbed response.*\n\n"
            "Ask me anything about your transactions and I’ll help once the backend is plugged in!"
        )

###############################################################################
# Data helpers (stub until Tapix API is connected)                            #
###############################################################################

def _load_sample_data() -> pd.DataFrame:  # noqa: D401 – simple function
    """Return a tiny sample of fake transactions so the UI always renders."""
    return pd.DataFrame(
        [
            {"date": "2025‑07‑01", "merchant": "Starbucks", "category": "Food & Drink", "amount": -4.50},
            {"date": "2025‑07‑02", "merchant": "H&M", "category": "Fashion", "amount": -39.90},
            {"date": "2025‑07‑03", "merchant": "Netflix", "category": "Digital Services", "amount": -15.99},
            {"date": "2025‑07‑04", "merchant": "Salary", "category": "Income", "amount": 2500.00},
            {"date": "2025‑07‑05", "merchant": "Esso", "category": "Car", "amount": -58.11},
            {"date": "2025‑07‑06", "merchant": "Ikea", "category": "House & Garden", "amount": -118.51},
        ]
    )


def fetch_tapix_data() -> pd.DataFrame:
    """Stub for Tapix API – replace with real call when ready."""
    # TODO: Use your Tapix.io credentials and fetch real enriched data.
    return _load_sample_data()

###############################################################################
# Streamlit page config & global style                                       #
###############################################################################

st.set_page_config(
    page_title="Tapix AI Finance Assistant",
    page_icon="💸",
    layout="wide",
)

# ---------------------------------------------------------------------------
# 🔥  One‑shot CSS injection to make everything look *so* much better.
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    /* === Base reset === */
    #MainMenu, footer {visibility: hidden;}

    /* === Page background – Tapix green gradient === */
    .stApp {
        background: linear-gradient(135deg, #2CC87F 0%, #10B981 35%, #099D95 100%) fixed;
        color: #ffffff;
        font-family: "Inter", sans-serif;
    }

    /* === Sidebar tweaks === */
    .stSidebar {
        background: transparent;
    }
    section[data-testid="stSidebar"], .stSidebarContent {
        background: rgba(255, 255, 255, 0.10) !important;
        backdrop-filter: blur(8px);
        border-radius: 1rem;
    }

    /* === Metric cards === */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 0.75rem;
        padding: 1.25rem 1rem 1rem;
        text-align: center;
        margin-bottom: 1.25rem;
        box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.05) inset;
    }
    div[data-testid="metric-container"] label {
        color: #D1FAE5;
        font-weight: 600;
    }
    div[data-testid="metric-container"] div:nth-child(2) {
        color: #ffffff;
        font-size: 1.4rem;
        font-weight: 700;
    }

    /* === Chat messages (glassmorphism) === */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.09);
        border: none;
        border-radius: 1rem;
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(6px);
    }
    .stChatMessage.user {
        background: rgba(255, 255, 255, 0.20);
    }
    .stChatMessage.assistant {
        background: rgba(0, 0, 0, 0.20);
    }

    /* === Primary buttons (suggestions + others) === */
    button[data-testid="baseButton-primary"] {
        background: #ffffff !important;
        color: #0F766E !important;
        border: none;
        border-radius: 999px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.06);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    button[data-testid="baseButton-primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.12);
    }

    /* === DataFrame (optional) === */
    .dataframe {background: rgba(255,255,255,0.12);}  /* when used */
    </style>
    """,
    unsafe_allow_html=True,
)

###############################################################################
# Session state & initial system prompt                                      #
###############################################################################

if "messages" not in st.session_state:
    st.session_state["messages"]: List[Dict[str, str]] = [
        {
            "role": "system",
            "content": (
                "You are Tapix, a friendly AI finance assistant. "
                "You have access to the user’s transaction history and can help "
                "them understand spending, budgets, and trends."
            ),
        }
    ]

###############################################################################
# Data + sidebar quick stats                                                 #
###############################################################################

transactions: pd.DataFrame = fetch_tapix_data()

# --- Quick stats in sidebar -------------------------------------------------
st.sidebar.title("🪙 Quick stats")

month_label = datetime.now().strftime("%B %Y")
month_spend = transactions.loc[transactions.amount < 0, "amount"].sum()

# Biggest spending category this month
biggest_cat = (
    transactions.loc[transactions.amount < 0]
    .groupby("category")["amount"]
    .sum()
    .abs()
    .idxmax()
)

st.sidebar.metric(f"{month_label} Spending", f"€{-month_spend:,.0f}")
st.sidebar.metric("Top Category", biggest_cat)
st.sidebar.metric("Transactions Analysed", len(transactions))

###############################################################################
# Main chat UI                                                               #
###############################################################################

st.title("💬 Tapix AI Assistant")

# --- Existing conversation --------------------------------------------------
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Quick‑query suggestion buttons ----------------------------------------
_suggestions = [
    "How much have I spent on coffee this month?",
    "Where did most of my money go last week?",
    "What is my biggest subscription?",
]

st.markdown("**Quick questions:**")
col_objs = st.columns(len(_suggestions))
selected_suggestion: Optional[str] = None
for col, txt in zip(col_objs, _suggestions):
    if col.button(txt, use_container_width=True):
        selected_suggestion = txt

# --- Chat input -------------------------------------------------------------
user_input = selected_suggestion or st.chat_input("Ask me anything about your money…")

if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate assistant reply
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            reply: str = generate_ai_response(
                st.session_state["messages"],
                extra_context={"transactions": transactions.to_dict("records")},
            )
            st.markdown(reply)

    st.session_state["messages"].append({"role": "assistant", "content": reply})
