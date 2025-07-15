"""
Tapix.io – AI Financial Assistant (Streamlit prototype)
=====================================================
A one–file Streamlit application replicating the HTML mock‑up you shared while
adding real chat behaviour, a sidebar with quick stats, and sample data so the
app is runnable out‑of‑the‑box. Replace the stub functions with real calls to
Tapix and your favourite LLM when you are ready.

How to run locally
------------------
$ pip install streamlit 
$ streamlit run app.py

For deployment to Streamlit Cloud or a GitHub Actions workflow, keep this file
at the repository root and declare the Python version you need in a
`requirements.txt` (e.g. `streamlit==1.35.0`).
"""

from __future__ import annotations

import datetime as _dt
from typing import List, Dict

import streamlit as st

###############################################################################
# Page set‑up & global styles
###############################################################################

st.set_page_config(
    page_title="Tapix.io – AI Financial Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Light touch CSS just to soften Streamlit’s default look -------------- #
CUSTOM_CSS = """
<style>
/* Reduce padding around main container */
section.main > div { padding-top: 1.5rem; }

/* Nice dark gradient background */
body {
    background: radial-gradient(ellipse at top, #0a0e27 0%, #141830 80%);
    color: #ffffff;
}

/* Hide default Streamlit footer */
footer { visibility: hidden; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

###############################################################################
# Demo data (replace with live Tapix enrichment once API keys are wired‑up)
###############################################################################

Transaction = Dict[str, str | float]

transaction_data: Dict[str, Dict[str, str | List[Transaction]]] = {
    "tesco": {
        "merchant": "Tesco",
        "category": "Groceries",
        "transactions": [
            {"date": "2025-07-12", "amount": 47.83, "items": ["Weekly shop"]},
            {"date": "2025-07-05", "amount": 23.45, "items": ["Quick shop"]},
            {"date": "2025-06-28", "amount": 89.20, "items": ["Monthly shop"]},
            {"date": "2025-06-21", "amount": 15.60, "items": ["Snacks"]},
            {"date": "2025-06-14", "amount": 124.50, "items": ["BBQ supplies"]},
        ],
    },
    "amazon": {
        "merchant": "Amazon",
        "category": "Shopping",
        "transactions": [
            {"date": "2025-07-11", "amount": 45.99, "items": ["Electronics"]},
            {"date": "2025-07-03", "amount": 23.49, "items": ["Books"]},
            {"date": "2025-06-20", "amount": 89.99, "items": ["Gifts"]},
        ],
    },
    "netflix": {
        "merchant": "Netflix",
        "category": "Entertainment",
        "transactions": [
            {"date": "2025-07-01", "amount": 15.99, "items": ["Monthly subscription"]},
            {"date": "2025-06-01", "amount": 15.99, "items": ["Monthly subscription"]},
        ],
    },
}

###############################################################################
# Helper functions
###############################################################################

def _sum_month(merchant_transactions: List[Transaction], year_month: str) -> float:
    """Sum the amounts for a list of transactions in YYYY‑MM."""
    return sum(t["amount"] for t in merchant_transactions if t["date"].startswith(year_month))


def get_quick_stats(data: Dict[str, Dict]) -> tuple[float, str, int]:
    """Return (this_month_spend, top_category, transaction_count)."""
    ym = _dt.date.today().strftime("%Y-%m")
    month_total = 0.0
    category_totals: Dict[str, float] = {}
    tx_count = 0

    for merchant in data.values():
        merchant_total = sum(t["amount"] for t in merchant["transactions"])
        month_total += _sum_month(merchant["transactions"], ym)
        category_totals[merchant["category"]] = (
            category_totals.get(merchant["category"], 0.0) + merchant_total
        )
        tx_count += len(merchant["transactions"])

    top_category = max(category_totals, key=category_totals.get)
    return month_total, top_category, tx_count


def generate_ai_response(message: str) -> str:
    """Very small rule‑based generator to mimic AI behaviour.

    Swap this for a real LLM call – e.g. to OpenAI or Azure – once you have
    keyed up your environment variables.
    """

    lower = message.lower()

    if "tesco" in lower:
        d = transaction_data["tesco"]
        total = sum(t["amount"] for t in d["transactions"])
        this_month_total = _sum_month(d["transactions"], _dt.date.today().strftime("%Y-%m"))
        average = total / len(d["transactions"])

        rows = "\n".join(
            f"<li>£{t['amount']:.2f} on {_dt.datetime.strptime(t['date'], '%Y-%m-%d').strftime('%d %b')} – {t['items'][0]}</li>"
            for t in d["transactions"][:3]
        )

        return f"""
            <p><strong>🛒 Tesco spending overview</strong></p>
            <ul>{rows}</ul>
            <p><strong>This month:</strong> £{this_month_total:.2f}<br>
               <strong>Average transaction:</strong> £{average:.2f}</p>
            <p>📉 Your grocery spending is 15 % lower than last month – nice job keeping it in check!</p>
        """

    if "subscription" in lower or "recurring" in lower:
        return """
            <p><strong>🔄 Recurring subscriptions</strong></p>
            <ul>
                <li>Netflix – £15.99 / month (1st)</li>
                <li>Spotify – £9.99 / month (10th)</li>
                <li>Amazon Prime – £95.00 / year</li>
            </ul>
            <p>Total monthly: £25.98<br>
            💡 Consider reviewing these to make sure you still need them!</p>
        """

    if "amazon" in lower:
        return """
            <p><strong>📦 Amazon spending</strong></p>
            <p>You've spent £159.47 on Amazon in the last 30 days across 3 transactions – roughly 23 % more than the previous month.</p>
            <p>Most of those purchases are in <em>Electronics</em>.</p>
        """

    # Fallback
    return (
        "I can help you analyse your spending. Try questions like:\n"
        "• 'How much did I spend at Tesco this month?'\n"
        "• 'What's my average weekly grocery spend?'\n"
        "• 'Show me restaurant expenses for the last 3 months'\n"
        "• 'Am I spending more on Amazon compared to last month?'\n"
        "• 'What subscriptions repeat every month?'\n"
    )


###############################################################################
# Sidebar – quick overview & sample queries
###############################################################################

month_spend, top_category, tx_count = get_quick_stats(transaction_data)

with st.sidebar:
    st.markdown("## ⚡ tapix.io")
    st.caption("AI‑Powered Financial Assistant")

    st.divider()
    st.subheader("📊 Quick overview")
    st.metric("This month's spending", f"£{month_spend:,.2f}")
    st.metric("Top category", top_category)
    st.metric("Transactions analysed", tx_count)

    st.divider()
    st.subheader("💡 Try asking")
    sample_qs = [
        "How much did I spend at Tesco this month?",
        "What's my average weekly spending on groceries?",
        "Show me my restaurant expenses for the last 3 months",
        "Am I spending more on Amazon compared to last month?",
        "What are my recurring subscriptions?",
    ]

    for q in sample_qs:
        if st.button(q, key=q):
            st.session_state["queued_prompt"] = q

###############################################################################
# Chat area
###############################################################################

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "ai",
            "content": (
                "Hello! I'm your AI financial assistant powered by Tapix. I can help you\n"
                "understand your spending patterns, track expenses, and provide insights\n"
                "about your finances.\n\n"
                "**What I can do**\n"
                "- Analyse spending at specific merchants (e.g. *Tesco*)\n"
                "- Track category budgets (e.g. *Food*)\n"
                "- Compare periods (e.g. *last month vs this month*)\n"
                "- Identify recurring payments and subscriptions\n"
                "- Surface personalised saving tips\n"
            ),
        }
    ]

# Render history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"], unsafe_allow_html=True)

#– Handle new prompt either from sidebar shortcut or chat input –#
prompt: str | None = st.session_state.pop("queued_prompt", None)

if prompt is None:
    prompt = st.chat_input("Ask me about your spending...")

if prompt:
    # 1️⃣ Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2️⃣ Generate AI reply (replace with real LLM call)
    response = generate_ai_response(prompt)

    st.session_state.messages.append({"role": "ai", "content": response})
    with st.chat_message("ai"):
        st.markdown(response, unsafe_allow_html=True)

###############################################################################
# Footer note
###############################################################################

st.caption("Demo powered by Streamlit · Data enrichment courtesy of Tapix.io")
