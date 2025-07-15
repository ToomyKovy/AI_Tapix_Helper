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

# --- Enhanced Glassmorphism CSS -----------------------------------------------
GLASSMORPHISM_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
/* ===== Base Styles & Variables ===== */
:root {
    --glass-bg: rgba(255, 255, 255, 0.25);
    --glass-border: rgba(255, 255, 255, 0.18);
    --glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    --hover-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.45);
    --primary: #7c3aed;
    --primary-light: rgba(124, 58, 237, 0.1);
    --primary-glass: rgba(124, 58, 237, 0.08);
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --backdrop-blur: blur(20px);
}

/* ===== Global Background ===== */
html, body, [class*="stApp"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    background-attachment: fixed;
    color: var(--text-primary);
    min-height: 100vh;
}

/* Animated background orbs */
[class*="stApp"]::before,
[class*="stApp"]::after {
    content: '';
    position: fixed;
    border-radius: 50%;
    background: radial-gradient(circle at 30% 80%, rgba(120, 119, 198, 0.3), transparent);
    filter: blur(40px);
    z-index: -1;
}

[class*="stApp"]::before {
    width: 400px;
    height: 400px;
    top: -200px;
    right: -100px;
    animation: float 20s ease-in-out infinite;
}

[class*="stApp"]::after {
    width: 300px;
    height: 300px;
    bottom: -150px;
    left: -50px;
    animation: float 15s ease-in-out infinite reverse;
}

@keyframes float {
    0%, 100% { transform: translate(0, 0) rotate(0deg); }
    33% { transform: translate(30px, -30px) rotate(120deg); }
    66% { transform: translate(-20px, 20px) rotate(240deg); }
}

/* ===== Main Container Glass Effect ===== */
.main .block-container {
    background: var(--glass-bg);
    backdrop-filter: var(--backdrop-blur);
    -webkit-backdrop-filter: var(--backdrop-blur);
    border-radius: 20px;
    border: 1px solid var(--glass-border);
    box-shadow: var(--glass-shadow);
    padding: 2rem;
    margin: 1rem;
}

/* ===== Hide Streamlit Elements ===== */
footer { visibility: hidden; }
header [data-testid="stToolbar"] { display: none !important; }
.reportview-container .main footer { display: none; }

/* ===== Sidebar Glass Effect ===== */
section[data-testid="stSidebar"] {
    background: var(--glass-bg);
    backdrop-filter: var(--backdrop-blur);
    -webkit-backdrop-filter: var(--backdrop-blur);
    border-right: 1px solid var(--glass-border);
}

section[data-testid="stSidebar"] > div {
    background: transparent;
}

/* ===== Chat Messages Glass Style ===== */
[data-testid="stChatMessage"] {
    background: transparent !important;
    padding: 0 !important;
}

.chat-bubble {
    backdrop-filter: var(--backdrop-blur);
    -webkit-backdrop-filter: var(--backdrop-blur);
    border: 1px solid var(--glass-border);
    box-shadow: var(--glass-shadow);
    border-radius: 20px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.chat-bubble::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%);
    pointer-events: none;
}

.chat-bubble:hover {
    transform: translateY(-2px);
    box-shadow: var(--hover-shadow);
    border-color: rgba(255, 255, 255, 0.25);
}

.chat-user {
    background: linear-gradient(135deg, rgba(124, 58, 237, 0.15) 0%, rgba(124, 58, 237, 0.05) 100%);
    margin-left: auto;
    max-width: 80%;
}

.chat-assistant {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.35) 0%, rgba(255, 255, 255, 0.15) 100%);
    margin-right: auto;
    max-width: 80%;
}

/* ===== Chat Input Glass Style ===== */
[data-testid="stChatInput"] > div {
    background: var(--glass-bg) !important;
    backdrop-filter: var(--backdrop-blur) !important;
    -webkit-backdrop-filter: var(--backdrop-blur) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 15px !important;
    box-shadow: var(--glass-shadow) !important;
    transition: all 0.3s ease !important;
}

[data-testid="stChatInput"] > div:focus-within {
    border-color: rgba(124, 58, 237, 0.3) !important;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.1), var(--hover-shadow) !important;
}

/* ===== Metrics Glass Cards ===== */
[data-testid="metric-container"] {
    background: var(--glass-bg);
    backdrop-filter: var(--backdrop-blur);
    -webkit-backdrop-filter: var(--backdrop-blur);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 1.2rem;
    box-shadow: var(--glass-shadow);
    transition: all 0.3s ease;
}

[data-testid="metric-container"]:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: var(--hover-shadow);
}

[data-testid="metric-container"] label {
    color: var(--text-secondary);
    font-weight: 500;
    font-size: 0.875rem;
    letter-spacing: 0.025em;
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    background: linear-gradient(135deg, var(--primary) 0%, #a855f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
}

/* ===== Tabs Glass Style ===== */
[data-testid="stTabs"] {
    background: transparent;
}

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: var(--glass-bg);
    backdrop-filter: var(--backdrop-blur);
    -webkit-backdrop-filter: var(--backdrop-blur);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}

[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent;
    color: var(--text-secondary);
    border-radius: 8px;
    transition: all 0.3s ease;
}

[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    background: rgba(255, 255, 255, 0.1);
}

[data-testid="stTabs"] [aria-selected="true"] {
    background: rgba(255, 255, 255, 0.3) !important;
    color: var(--text-primary) !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* ===== Buttons Glass Style ===== */
.stButton > button {
    background: var(--glass-bg);
    backdrop-filter: var(--backdrop-blur);
    -webkit-backdrop-filter: var(--backdrop-blur);
    border: 1px solid var(--glass-border);
    color: var(--primary);
    border-radius: 12px;
    padding: 0.75rem 1.5rem;
    font-weight: 500;
    box-shadow: var(--glass-shadow);
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background: rgba(124, 58, 237, 0.1);
    border-color: rgba(124, 58, 237, 0.3);
    transform: translateY(-2px);
    box-shadow: var(--hover-shadow);
}

/* ===== Dataframe Glass Style ===== */
[data-testid="stDataFrame"] {
    background: var(--glass-bg);
    backdrop-filter: var(--backdrop-blur);
    -webkit-backdrop-filter: var(--backdrop-blur);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: var(--glass-shadow);
}

[data-testid="stDataFrame"] table {
    background: transparent !important;
}

[data-testid="stDataFrame"] th {
    background: rgba(124, 58, 237, 0.05) !important;
    backdrop-filter: var(--backdrop-blur);
    font-weight: 600;
    color: var(--text-primary);
}

[data-testid="stDataFrame"] td {
    background: transparent !important;
    border-color: var(--glass-border) !important;
}

[data-testid="stDataFrame"] tr:hover td {
    background: rgba(124, 58, 237, 0.03) !important;
}

/* ===== Progress Bars Glass Style ===== */
[data-testid="stProgress"] > div {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    overflow: hidden;
}

[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, var(--primary) 0%, #a855f7 100%);
    box-shadow: 0 2px 8px rgba(124, 58, 237, 0.3);
}

/* ===== Select Box Glass Style ===== */
[data-baseweb="select"] > div {
    background: var(--glass-bg) !important;
    backdrop-filter: var(--backdrop-blur) !important;
    -webkit-backdrop-filter: var(--backdrop-blur) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    box-shadow: var(--glass-shadow) !important;
}

[data-baseweb="select"] > div:hover {
    border-color: rgba(124, 58, 237, 0.3) !important;
}

/* ===== Date Input Glass Style ===== */
[data-testid="stDateInput"] > div > div {
    background: var(--glass-bg) !important;
    backdrop-filter: var(--backdrop-blur) !important;
    -webkit-backdrop-filter: var(--backdrop-blur) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
}

/* ===== Info/Warning/Error Glass Style ===== */
[data-testid="stAlert"] {
    background: var(--glass-bg);
    backdrop-filter: var(--backdrop-blur);
    -webkit-backdrop-filter: var(--backdrop-blur);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    box-shadow: var(--glass-shadow);
}

/* ===== Spinner Glass Style ===== */
[data-testid="stSpinner"] > div {
    border-color: var(--primary) transparent transparent transparent !important;
}

/* ===== Typography ===== */
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary);
    font-weight: 600;
    letter-spacing: -0.02em;
}

/* ===== Scrollbar Styling ===== */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 5px;
}

::-webkit-scrollbar-thumb {
    background: rgba(124, 58, 237, 0.3);
    border-radius: 5px;
    transition: background 0.3s ease;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(124, 58, 237, 0.5);
}

/* ===== Responsive Design ===== */
@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem;
        margin: 0.5rem;
    }
    
    .chat-bubble {
        max-width: 95%;
    }
}
</style>
"""

st.markdown(GLASSMORPHISM_CSS, unsafe_allow_html=True)

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

# Load transaction data
@st.cache_data
def load_transactions():
    data_file = Path("sample_transactions.csv")
    if data_file.exists():
        df = pd.read_csv(data_file, parse_dates=["date"])
        df = df.sort_values("date", ascending=False)
        return df
    else:
        return pd.DataFrame(columns=["date", "amount", "category", "description", "merchant"])

df = load_transactions()

################################################################################
# Sidebar – quick metrics
################################################################################

with st.sidebar:
    st.markdown("### 📊 Quick snapshot")

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
        
        # Category breakdown
        st.markdown("### 📈 Category Breakdown")
        if not current_month.empty:
            cat_summary = current_month.groupby("category")["amount"].sum().sort_values(ascending=False)
            for cat, amt in cat_summary.items():
                pct = (amt / month_total * 100) if month_total > 0 else 0
                st.progress(pct / 100, text=f"{cat}: ${amt:.2f} ({pct:.1f}%)")
    else:
        st.info("No transaction data loaded yet. Make sure 'sample_transactions.csv' exists.")

    st.markdown("""---
    Made with ❤️ by **Tapix** + **OpenAI**
    """)

################################################################################
# Main area with tabs
################################################################################

tab1, tab2 = st.tabs(["💬 AI Chat", "📋 Transactions"])

with tab1:
    st.markdown("## Chat with your finances", unsafe_allow_html=True)

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

        # 3) Call backend AI in a spinner, passing transaction data as context
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                try:
                    # Create context from transaction data
                    extra_context = {}
                    if not df.empty:
                        extra_context = {
                            "total_transactions": len(df),
                            "date_range": f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}",
                            "total_spent": f"${df['amount'].sum():,.2f}",
                            "categories": df['category'].unique().tolist(),
                            "recent_transactions": df.head(10).to_dict('records')
                        }
                    
                    reply = generate_ai_response(
                        st.session_state["messages"], 
                        extra_context=extra_context
                    )
                except Exception as e:
                    reply = f"⚠️ Sorry, I couldn't reach the AI service right now. Error: {str(e)}"

            st.markdown(f'<div class="chat-bubble chat-assistant">{reply}</div>', unsafe_allow_html=True)

        # 4) Save assistant reply & rerun to refresh history
        st.session_state["messages"].append({"role": "assistant", "content": reply})
        st.rerun()

with tab2:
    st.markdown("## 📋 Transaction History", unsafe_allow_html=True)
    
    if not df.empty:
        # Date filter
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=df["date"].min())
        with col2:
            end_date = st.date_input("End Date", value=df["date"].max())
        
        # Category filter
        categories = ["All"] + sorted(df["category"].unique().tolist())
        selected_category = st.selectbox("Filter by Category", categories)
        
        # Filter data
        filtered_df = df[(df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)]
        if selected_category != "All":
            filtered_df = filtered_df[filtered_df["category"] == selected_category]
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Spent", f"${filtered_df['amount'].sum():,.2f}")
        with col2:
            st.metric("Avg Transaction", f"${filtered_df['amount'].mean():,.2f}" if not filtered_df.empty else "$0.00")
        with col3:
            st.metric("Transaction Count", f"{len(filtered_df):,}")
        
        # Transaction table
        st.markdown("### Recent Transactions")
        if not filtered_df.empty:
            # Format the dataframe for display
            display_df = filtered_df.copy()
            display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
            display_df["amount"] = display_df["amount"].apply(lambda x: f"${x:,.2f}")
            
            # Rename columns for better display
            display_df = display_df.rename(columns={
                "date": "Date",
                "amount": "Amount",
                "category": "Category",
                "description": "Description",
                "merchant": "Merchant"
            })
            
            st.dataframe(
                display_df[["Date", "Amount", "Category", "Description", "Merchant"]], 
                use_container_width=True,
                hide_index=True
            )
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download All Transactions",
                data=csv,
                file_name=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No transactions found for the selected filters.")
    else:
        st.warning("⚠️ No transaction data available. Please ensure 'sample_transactions.csv' exists in your project directory.")

################################################################################
# End of script
################################################################################