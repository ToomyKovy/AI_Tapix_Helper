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
    # Remove the sidebar width slider
    # Add a draggable handle and JS for resizing
    st.markdown("""
    <style>
    #custom-sidebar-resizer {
        position: absolute;
        top: 0;
        right: 0;
        width: 8px;
        height: 100vh;
        cursor: ew-resize;
        z-index: 1000;
        background: transparent;
    }
    section[data-testid='stSidebar'] {
        position: relative !important;
    }
    </style>
    <div id="custom-sidebar-resizer"></div>
    <script>
    const resizer = window.parent.document.getElementById('custom-sidebar-resizer');
    const sidebar = window.parent.document.querySelector('section[data-testid="stSidebar"]');
    let isResizing = false;
    let startX = 0;
    let startWidth = 0;
    if (resizer && sidebar) {
        resizer.onmousedown = function(e) {
            isResizing = true;
            startX = e.clientX;
            startWidth = sidebar.offsetWidth;
            document.body.style.cursor = 'ew-resize';
        };
        window.parent.document.onmousemove = function(e) {
            if (!isResizing) return;
            let newWidth = startWidth + (e.clientX - startX);
            newWidth = Math.max(250, Math.min(newWidth, 600));
            sidebar.style.width = newWidth + 'px';
            sidebar.style.minWidth = newWidth + 'px';
            sidebar.style.maxWidth = newWidth + 'px';
        };
        window.parent.document.onmouseup = function() {
            isResizing = false;
            document.body.style.cursor = '';
        };
    }
    </script>
    """, unsafe_allow_html=True)
    df = st.session_state["df"]
    if not df.empty:
        # Remove the glass-metrics container div
        st.markdown('<div class="glass-metrics-heading">Quick Snapshot</div>', unsafe_allow_html=True)
        months = df["date"].dt.to_period("M").sort_values().unique()
        current_period = pd.Timestamp.now().to_period("M")
        month_strs = [str(m) for m in months]
        default_index = month_strs.index(str(current_period)) if str(current_period) in month_strs else len(month_strs) - 1
        selected_month = st.selectbox("", month_strs, index=default_index, label_visibility="collapsed")
        selected_period = pd.Period(selected_month)
        current_month = df[df["date"].dt.to_period("M") == selected_period]

        month_total = current_month["amount"].sum() if not current_month.empty else 0
        top_cat = (
            current_month.groupby("category")["amount"].sum().sort_values(ascending=False).head(1).index[0]
            if not current_month.empty else "–"
        )
        st.metric("This Month's Spend", f"${month_total:,.2f}")
        st.metric("Top Category", top_cat)
        st.metric("Transactions Analysed", f"{len(current_month):,}")

        # Glassmorphism box for pie chart
        if not current_month.empty:
            import plotly.express as px
            cat_summary = current_month.groupby("category")['amount'].sum().sort_values(ascending=False)
            customdata = []
            for cat in cat_summary.index:
                txs = current_month[current_month['category'] == cat]
                tx_list = [f"{row['date'].strftime('%Y-%m-%d')}: ${row['amount']:.2f} - {row['description']}" for _, row in txs.iterrows()]
                customdata.append('<br>'.join(tx_list))
            fig = px.pie(
                names=cat_summary.index,
                values=cat_summary.values,
                hole=0.3,
                color_discrete_sequence=[
                    '#a5d8ff', '#b2f2bb', '#ffd6a5', '#ffadad', '#cdb4db', '#b5ead7', '#f3c4fb', '#fdffb6', '#bdb2ff', '#b0efeb'
                ]
            )
            fig.update_traces(
                pull=[0.08]*len(cat_summary),
                customdata=customdata,
                hovertemplate="<b>%{label}</b><br>Amount: $%{value:,.2f}<br>Percent: %{percent}<br><br><b>Transactions:</b><br>%{customdata}<extra></extra>",
                textinfo='label+percent',
                marker=dict(line=dict(color='white', width=2))
            )
            fig.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.markdown("<h4 style='margin-top:0'>📈 Category Breakdown</h4>", unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning('No data loaded from sample_transactions.csv. Please check the file.')

################################################################################
# Main area with tabs
################################################################################

df = st.session_state["df"]
tab1, tab2 = st.tabs(["💬 AI Chat", "📋 Transactions"])

with tab1:
    st.markdown("## Chat with your finances", unsafe_allow_html=True)

    # Suggested questions as fully custom HTML glassmorphism buttons
    import streamlit.components.v1 as components
    suggested_questions = [
        "How much did I spend on groceries last month?",
        "What was my biggest expense in March?",
        "Show me a summary of my spending by category.",
        "Did I spend more this month than last month?",
        "Are there any unusual transactions this week?",
        "How much did I spend at Starbucks?"
    ]
    # Render as HTML buttons with a form
    st.markdown('''
    <form id="suggested-form">
      <div class="suggested-btn-row" style="display: flex; flex-wrap: wrap; gap: 0.5rem 0.5rem; margin-bottom: 1rem;">
    ''' , unsafe_allow_html=True)
    for idx, q in enumerate(suggested_questions):
        st.markdown(
            f'''<button type="submit" name="suggested" value="{q}" class="glass-button" style="background: var(--glass-bg); color: #fff; border: none; border-radius: 16px; padding: 0.5rem 1.2rem; font-weight: 500; font-size: 1rem; margin-bottom: 0; margin-right: 0.5rem; margin-top: 0.2rem; margin-left: 0; box-shadow: 0 8px 32px 0 rgba(31,38,135,0.10); cursor: pointer;">{q}</button>''',
            unsafe_allow_html=True
        )
    st.markdown('''</div></form>''', unsafe_allow_html=True)

    # JavaScript to capture which button was clicked and set a Streamlit variable
    components.html('''
    <script>
    const form = window.parent.document.querySelector('#suggested-form');
    if (form) {
        form.onsubmit = function(e) {
            e.preventDefault();
            const btn = e.submitter;
            if (btn && btn.value) {
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: btn.value}, '*');
            }
        }
    }
    window.addEventListener('message', (event) => {
        if (event.data.type === 'streamlit:setComponentValue') {
            window.parent.postMessage({isStreamlitMessage: true, type: 'streamlit:setComponentValue', value: event.data.value}, '*');
        }
    });
    </script>
    ''', height=0)

    # Use Streamlit's session state to receive the value
    if 'suggested_question' not in st.session_state:
        st.session_state['suggested_question'] = ''
    selected_question = st.query_params.get('suggested', [''])[0]
    if selected_question:
        st.session_state['suggested_question'] = selected_question
        st.session_state["messages"].append({"role": "user", "content": selected_question})
        try:
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
        st.session_state["messages"].append({"role": "assistant", "content": reply})
        st.query_params.clear()  # Clear the param
        st.rerun()

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