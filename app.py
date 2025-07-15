"""app.py – Tapix AI Finance Assistant (premium Streamlit UI)
================================================================
A polished Streamlit front‑end that chats with `backend.py` (OpenAI v1)
while showing instant spending metrics. Uses **st.rerun()** – compatible
with Streamlit ≥ 1.27.  Drop the file in your repo, push, and redeploy.

Deploy on Streamlit Cloud:
    1. Add your OPENAI_API_KEY in Secrets.
    2. Push this repo and deploy.
"""

from __future__ import annotations
import os
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st

if "OPENAI_API_KEY" in st.secrets:
    os.environ.setdefault("OPENAI_API_KEY", st.secrets["OPENAI_API_KEY"])

from backend import generate_ai_response

################################################################################
# Streamlit page & theme
################################################################################

st.set_page_config(
    page_title="Tapix AI Finance Assistant",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Load External CSS ---------------------------------------------------------
def load_css(file_path: str = "styles.css") -> str:
    """Load CSS from external file with fallback to basic styles."""
    css_file = Path(file_path)
    
    if css_file.exists():
        return css_file.read_text()
    else:
        # Fallback CSS if external file doesn't exist
        return """
        <style>
        html, body, [class*="stApp"] {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f5f7fa;
        }
        .chat-bubble {
            border-radius: 1rem;
            padding: 1rem;
            margin-bottom: 0.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .chat-user {
            background: #e3f2fd;
            margin-left: auto;
            max-width: 80%;
        }
        .chat-assistant {
            background: #ffffff;
            margin-right: auto;
            max-width: 80%;
        }
        footer {visibility: hidden;}
        </style>
        """

# Apply CSS
css_content = load_css()
st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

################################################################################
# Session state initialisation
################################################################################

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "👋 **Welcome!** Ask me anything about your spending – for example, *'How much did I spend on coffee this month?'*",
        }
    ]

################################################################################
# Sidebar – quick metrics
################################################################################

with st.sidebar:
    st.markdown("### 📊 Quick snapshot")

    # Load sample data (CSV bundled) or empty df
    data_file = Path("sample_transactions.csv")
    if data_file.exists():
        df = pd.read_csv(data_file, parse_dates=["date"])
    else:
        df = pd.DataFrame(columns=["date", "amount", "category"])

    if not df.empty:
        current_month = df[df["date"].dt.to_period("M") == datetime.today().date().replace(day=1).strftime("%Y-%m")]
        month_total = current_month["amount"].sum()
        top_cat = (
            current_month.groupby("category")["amount"].sum().sort_values(ascending=False).head(1).index[0]
            if not current_month.empty else "–"
        )

        st.metric("This Month's Spend", f"${month_total:,.2f}")
        st.metric("Top Category", top_cat)
        st.metric("Transactions Analysed", f"{len(df):,}")
    else:
        st.info("No transaction data loaded yet.")

    st.markdown("""---
    Made with ❤️ by **Tapix** + **OpenAI**
    """)

################################################################################
# Main chat area
################################################################################

st.markdown("## 💬 Chat with your finances", unsafe_allow_html=True)

# Display message history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        bubble_cls = "chat-user" if msg["role"] == "user" else "chat-assistant"
        st.markdown(f'<div class="chat-bubble {bubble_cls}">{msg["content"]}</div>', unsafe_allow_html=True)

# Chat input
prompt = st.chat_input("Type your question and press Enter…")

if prompt:
    # 1) Save user prompt
    st.session_state["messages"].append({"role": "user", "content": prompt})

    # 2) Display user bubble immediately
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-bubble chat-user">{prompt}</div>', unsafe_allow_html=True)

    # 3) Call backend AI in a spinner
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                reply = generate_ai_response(st.session_state["messages"])
            except Exception:
                reply = "⚠️ Sorry, I couldn't reach the AI service right now. Please try again in a bit."

        st.markdown(f'<div class="chat-bubble chat-assistant">{reply}</div>', unsafe_allow_html=True)

    # 4) Save assistant reply & rerun to refresh history
    st.session_state["messages"].append({"role": "assistant", "content": reply})
    st.rerun()

################################################################################
# End of script
################################################################################