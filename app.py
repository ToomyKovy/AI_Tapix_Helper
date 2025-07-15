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

# Inject glassmorphism CSS from styles.css
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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

# Use session state for transaction data
if "df" not in st.session_state:
    st.session_state["df"] = df

################################################################################
# Sidebar – quick metrics
################################################################################

with st.sidebar:
    st.markdown("### 📊 Quick snapshot")

    # CSV upload feature
    uploaded_file = st.file_uploader("Upload your transactions CSV", type=["csv"])
    if uploaded_file:
        try:
            uploaded_df = pd.read_csv(uploaded_file, parse_dates=["date"])
            st.session_state["df"] = uploaded_df
            st.success("Transactions loaded!")
        except Exception as e:
            st.error(f"Failed to load CSV: {e}")

    df = st.session_state["df"]

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

df = st.session_state["df"]
tab1, tab2 = st.tabs(["💬 AI Chat", "📋 Transactions"])

with tab1:
    st.markdown("## Chat with your finances", unsafe_allow_html=True)

    # Suggested questions
    st.markdown("**Try asking:**")
    st.markdown("- How much did I spend on groceries last month?")
    st.markdown("- What was my biggest expense in March?")
    st.markdown("- Show me a summary of my spending by category.")
    st.markdown("- Did I spend more this month than last month?")
    st.markdown("- Are there any unusual transactions this week?")
    st.markdown("- How much did I spend at Starbucks?")

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
                    reply = f"<span style='color:red;'>⚠️ Sorry, I couldn't reach the AI service right now.<br>Error: {str(e)}</span>"
            st.markdown(f'<div class="chat-bubble chat-assistant">{reply}</div>', unsafe_allow_html=True)

        # 4) Save assistant reply & rerun to refresh history
        st.session_state["messages"].append({"role": "assistant", "content": reply})
        st.rerun()

with tab2:
    st.markdown("## 📋 Transaction History", unsafe_allow_html=True)
    
    df = st.session_state["df"]
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
        st.warning("⚠️ No transaction data available. Please ensure 'sample_transactions.csv' exists in your project directory or upload a CSV file in the sidebar.")

################################################################################
# End of script
################################################################################