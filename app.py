"""app.py – Premium‑styled Tapix AI Finance Assistant
================================================
A polished Streamlit front‑end with custom fonts, glassmorphism cards, and
minimal chrome.  Works with `backend.py` (OpenAI v1) and sample / Tapix data.

Run locally:
    $ export OPENAI_API_KEY="sk‑..."
    $ pip install -r requirements.txt
    $ streamlit run app.py

Deployed on Streamlit Cloud → just push + redeploy.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict

import pandas as pd
import streamlit as st

from backend import generate_ai_response

###############################################################################
# Page & global style
###############################################################################

st.set_page_config(
    page_title="Tapix AI Finance Assistant",
    page_icon="💳",
    layout="wide",
)

# Inject premium CSS: Inter font, glass cards, custom chat bubbles, hide footer.
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

:root {
    --primary: #7b4cff;
    --radius: 1.25rem;
    --card-bg: rgba(255, 255, 255, 0.75);
    --card-blur: 12px;
}

/* ----- General app styles ----- */
body, div, .stMarkdown p, .stMarkdown li {
    font-family: 'Inter', sans-serif;
}

[data-testid="stSidebar"] > div:first-child {
    background: linear-gradient(180deg, #7b4cff 0%, #6a3eff 100%);
    color: #ffffff;
}

/* Main background */
[data-testid="stAppViewContainer"] > .main {
    background: radial-gradient(circle at top left, #f0f3ff 0%, #ffffff 60%);
}

/* Glassmorphism card for chat */
.chat-card {
    background: var(--card-bg);
    backdrop-filter: blur(var(--card-blur));
    -webkit-backdrop-filter: blur(var(--card-blur));
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: var(--radius);
    padding: 2rem 1.5rem 1rem 1.5rem;
    margin-bottom: 1rem;
}

/* Bubbles */
.message-user, .message-ai {
    padding: 0.75rem 1rem;
    border-radius: var(--radius);
    line-height: 1.4;
    max-width: 80%;
}

.message-user {
    background: var(--primary);
    color: #fff;
    margin-left: auto;
}

.message-ai {
    background: #ececff;
    color: #222;
    margin-right: auto;
}

/* Hide Streamlit footer */
footer {visibility: hidden;}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

###############################################################################
# Data helpers & initialization
###############################################################################

@st.cache_data
def load_sample_transactions() -> pd.DataFrame:
    csv_path = Path(__file__).with_suffix(".csv")
    if csv_path.exists():
        return pd.read_csv(csv_path)
    # Fallback inline sample
    data = {
        "date": ["2025-07-10", "2025-07-09", "2025-07-08", "2025-07-05", "2025-07-04"],
        "merchant": ["Netflix", "Starbucks", "Amazon", "Adidas", "Uber"],
        "amount": [-9.99, -4.5, -56.2, -89.0, -17.3],
        "category": ["Entertainment", "Coffee", "Shopping", "Shopping", "Transport"],
    }
    return pd.DataFrame(data)

transactions = load_sample_transactions()

###############################################################################
# Sidebar – quick stats & navigation
###############################################################################

with st.sidebar:
    st.markdown("## 💸 This Month")
    month_spend = transactions["amount"].sum()
    top_cat = transactions["category"].mode()[0]
    st.metric("Total Spend", f"${abs(month_spend):,.2f}")
    st.metric("Top Category", top_cat)
    st.markdown("---")
    st.markdown("### Suggested questions")
    SUGGESTIONS = [
        "How much have I spent on coffee this month?",
        "What’s my biggest expense this week?",
        "Predict my bills for next month.",
    ]
    for q in SUGGESTIONS:
        if st.button(q):
            if "messages" not in st.session_state:
                st.session_state["messages"] = []
            st.session_state["messages"].append({"role": "user", "content": q})
            st.experimental_rerun()

###############################################################################
# Main – chat interface
###############################################################################

st.markdown("# Tapix AI Finance Assistant")

# Initialise chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi! I’m your finance assistant. Ask me anything about your spending."}
    ]

# Display messages
for msg in st.session_state["messages"]:
    bubble_class = "message-user" if msg["role"] == "user" else "message-ai"
    st.markdown(f'<div class="chat-card {bubble_class}">{msg["content"]}</div>', unsafe_allow_html=True)

# Chat input
prompt = st.chat_input("Type your question...")
if prompt:
    st.session_state["messages"].append({"role": "user", "content": prompt})
    # Call backend with full history
    with st.spinner("Thinking..."):
        try:
            reply = generate_ai_response(st.session_state["messages"], extra_context={"transactions": transactions.to_dict("records")})
        except Exception as e:
            reply = "Sorry, I couldn’t reach the AI service right now."    
    st.session_state["messages"].append({"role": "assistant", "content": reply})
    st.experimental_rerun()

###############################################################################
# Footer hidden via CSS – nothing else needed
###############################################################################