"""app.py – Tapix AI Finance Assistant (Streamlit)
================================================
A single‑file Streamlit front‑end that works with **backend.py** to answer any
finance question using OpenAI and (eventually) real Tapix‑enriched
transactions.

Run locally:
    $ export OPENAI_API_KEY="sk‑..."   # your key
    $ pip install -r requirements.txt
    $ streamlit run app.py

Deployed on Streamlit Community Cloud, just add the secret **OPENAI_API_KEY**
and you’re live.
"""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import pandas as pd
import streamlit as st

from backend import generate_ai_response

###############################################################################
# Data helpers
###############################################################################

def _load_sample_data() -> pd.DataFrame:  # fallback if Tapix isn’t wired yet
    """Returns a tiny sample of fake 2025 transactions so the app always runs."""
    return pd.DataFrame(
        [
            {"date": "2025-07-01", "merchant": "Starbucks", "category": "Coffee", "amount": -4.50},
            {"date": "2025-07-02", "merchant": "Whole Foods", "category": "Groceries", "amount": -62.30},
            {"date": "2025-07-03", "merchant": "Netflix", "category": "Subscription", "amount": -15.99},
            {"date": "2025-07-04", "merchant": "Salary", "category": "Income", "amount": 2500.00},
            {"date": "2025-07-05", "merchant": "Apple Store", "category": "Tech", "amount": -199.99},
            {"date": "2025-07-06", "merchant": "McDonald’s", "category": "Eating Out", "amount": -9.80},
        ]
    )


def fetch_tapix_data() -> pd.DataFrame:
    """Stub for Tapix API – replace with real call when ready."""
    # TODO: Use your Tapix.io credentials and fetch real enriched data.
    return _load_sample_data()

###############################################################################
# Streamlit page config & state
###############################################################################

st.set_page_config(
    page_title="Tapix AI Finance Assistant",
    page_icon="💸",
    layout="wide",
)

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
# Load transactions and sidebar metrics
###############################################################################

transactions: pd.DataFrame = fetch_tapix_data()

# --- Quick stats in sidebar -------------------------------------------------
month_label = datetime.now().strftime("%B %Y")
month_spend = transactions.loc[transactions.amount < 0, "amount"].sum()

top_category = (
    transactions.loc[transactions.amount < 0]
    .groupby("category")["amount"]
    .sum()
    .abs()
    .idxmax()
)

st.sidebar.title("📊 Quick stats")
st.sidebar.metric(f"{month_label} Spending", f"${-month_spend:,.0f}")
st.sidebar.metric("Top Category", top_category)
st.sidebar.metric("Transactions Analysed", len(transactions))

###############################################################################
# Main chat UI
###############################################################################

st.title("💬 Tapix AI Assistant")

# Show existing conversation
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Suggested quick‑query buttons
suggestions = [
    "How much have I spent on coffee this month?",
    "Where did most of my money go last week?",
    "What is my biggest subscription?",
]

st.write("**Quick questions:**")
cols = st.columns(len(suggestions))
selected_suggestion: Optional[str] = None
for col, text in zip(cols, suggestions):
    if col.button(text):
        selected_suggestion = text

# Chat input (or suggested button)
user_input = selected_suggestion or st.chat_input(
    "Ask me anything about your money…"
)

if user_input:
    # Add user message to state and display it
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

    # Save assistant message to history
    st.session_state["messages"].append({"role": "assistant", "content": reply})
